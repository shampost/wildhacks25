from fastapi import APIRouter
from server.models import PlantRecognitionRequest, PlantRecognitionResponse, PlantInfo
from server.model_loader import load_model, load_class_mapping, preprocess_image, load_disease_model, preprocess_disease_image
import torch
import google.generativeai as genai
import os

router = APIRouter()

# Load model and class mapping at startup
model = load_model("server/model_best.pth.tar")
class_mapping = load_class_mapping("server/class_mapping.txt")

# New disease model
disease_model, disease_feature_extractor = load_disease_model("server/disease_model/")

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

        # Predict plant
        with torch.no_grad():
            outputs = model(input_tensor)
            predicted_class = torch.argmax(outputs, dim=1).item()

        # Map to species ID
        species_id = class_mapping.get(predicted_class, "Unknown")

        # Use species_id as plant name for Gemini query
        plant_info = query_gemini(f"Species {species_id}")
        plant_info.name = f"Species {species_id}"

        # 🦠 Disease detection (move here)
        inputs = preprocess_disease_image(request.image_data, disease_feature_extractor)

        with torch.no_grad():
            outputs = disease_model(**inputs)
            predicted_disease = torch.argmax(outputs.logits, dim=1).item()

        disease_status = "Diseased" if predicted_disease == 1 else "Healthy"

        # Optionally add disease status to response
        plant_info.disease_status = disease_status  # you'll need to add this field to your PlantInfo model

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

