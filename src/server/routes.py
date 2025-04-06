from fastapi import APIRouter
from server.models import PlantRecognitionRequest, PlantRecognitionResponse, PlantInfo
from server.model_loader import load_model, load_class_mapping, preprocess_image
import torch
import google.generativeai as genai
import os

router = APIRouter()

# Load model and class mapping at startup
model = load_model("app/model_best.pth.tar")
class_mapping = load_class_mapping("app/class_mapping.txt")

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_gemini = genai.GenerativeModel("gemini-pro")

# Query Gemini with plant name
def query_gemini(plant_name):
    prompt = (
        f"Give me information about the plant called '{plant_name}'. "
        "I need: the season it grows in, a description of the plant, and care instructions for it. "
        "Format the answer in JSON with the fields: season, description, care, scientific_name, origin, soil_type, sunlight, watering."
    )

    response = model_gemini.generate_content(prompt)
    try:
        # Gemini responses are strings, we parse JSON from it
        import json
        plant_data = json.loads(response.text)
        return PlantInfo(**plant_data)
    except Exception as e:
        # Fallback in case Gemini response is not parsable
        return PlantInfo(
            name=plant_name,
            season="Unknown",
            description="Gemini response parsing failed.",
            care="Unknown",
            scientific_name="Unknown",
            origin="Unknown",
            soil_type="Unknown",
            sunlight="Unknown",
            watering="Unknown"
        )


@router.post("/identify-plant", response_model=PlantRecognitionResponse)
async def identify_plant(request: PlantRecognitionRequest):
    try:
        # Preprocess input image
        input_tensor = preprocess_image(request.image_data)

        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            predicted_class = torch.argmax(outputs, dim=1).item()

        # Map to species ID
        species_id = class_mapping.get(predicted_class, "Unknown")

        # Use species_id as plant name for Gemini query (optional: map to real name from CSV)
        plant_info = query_gemini(f"Species {species_id}")
        plant_info.name = f"Species {species_id}"

        return PlantRecognitionResponse(
            success=True,
            plant=plant_info,
            message="Plant identified and information retrieved from Gemini."
        )

    except Exception as e:
        return PlantRecognitionResponse(
            success=False,
            message=f"Error identifying plant: {str(e)}"
        )