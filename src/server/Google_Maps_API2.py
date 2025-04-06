import base64
import urllib.parse
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
import json

app = Flask(__name__)
CORS(app)  # "allow all" while testing

MAPS_API_KEY = ""
GEMINI_API_KEY = ""
UNSPLASH_ACCESS_KEY = ""


@app.route("/get-satellite-image", methods=["POST"])
def get_satellite_image():
    data = request.get_json()
    if not data or "address" not in data:
        return jsonify({"error": "No address provided"}), 400

    address = data["address"]
    encoded_address = urllib.parse.quote(address)

    # 1) GEOCODE THE ADDRESS
    geocode_url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={encoded_address}&key={MAPS_API_KEY}"
    )
    geocode_response = requests.get(geocode_url, timeout=10)
    geocode_data = geocode_response.json()

    if geocode_data.get("status") != "OK" or not geocode_data.get("results"):
        return jsonify({"error": "Unable to geocode address"}), 400

    location = geocode_data["results"][0]["geometry"]["location"]
    coordinates = {"lat": location["lat"], "lng": location["lng"]}

    # 2) SATELLITE IMAGE (OPTIONAL)
    static_map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={encoded_address}&zoom=18&size=800x800&maptype=satellite&key={MAPS_API_KEY}"
    )
    image_response = requests.get(static_map_url, timeout=10)
    if image_response.status_code != 200:
        return jsonify({"error": "Failed to fetch satellite image"}), 500

    image_data = image_response.content
    base64_image = base64.b64encode(image_data).decode("utf-8")

    # 3) GEMINI PLANT RECOMMENDATIONS
    client = genai.Client(api_key=GEMINI_API_KEY)
    gemini_prompt = f"""
    You are an expert agronomist with deep knowledge of hyperlocal climate conditions.
    Given the region corresponding to the address: {address} (encoded as {encoded_address}), 
    recommend exactly three plants or crops that are best suited for growth in that region. 
    For each recommendation, include:
    - 'plantName': The common name of the plant.
    - 'scientificName': The scientific name of the plant.
    - 'reason': A concise one-sentence explanation of why this plant is ideal for the region.
    - 'careInstruction': A brief one-sentence plant care instruction.
    Return only a valid JSON array of exactly three objects with the keys 
    'plantName', 'scientificName', 'reason', and 'careInstruction'. 
    Do not include any additional text or commentary. 
    Make sure to output only the raw JSON and nothing more.
    """

    gemini_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=gemini_prompt.strip(),
    )

    # Remove backticks or other extraneous characters
    raw_gemini_output = gemini_response.text.strip().strip("`")

    prefix = "Gemini cleaned output:"
    if raw_gemini_output.startswith(prefix):
        raw_gemini_output = raw_gemini_output[len(prefix) :].strip()

    # Optional: If the output might sometimes start with "json" (lowercase or uppercase)
    if raw_gemini_output.lower().startswith("json"):
        raw_gemini_output = raw_gemini_output[4:].strip()

    # Attempt to parse the raw Gemini output as JSON
    try:
        plants = json.loads(raw_gemini_output)
    except Exception as e:
        return jsonify({"error": "Gemini output not valid JSON", "debug": str(e)}), 500

    # 4) OPTIONAL: UNSPLASH IMAGE LOOKUP FOR EACH PLANT
    for plant in plants:
        query = urllib.parse.quote(f"{plant['plantName']} plant")
        unsplash_url = (
            f"https://api.unsplash.com/search/photos?"
            f"query={query}&per_page=1&client_id={UNSPLASH_ACCESS_KEY}"
        )
        resp = requests.get(unsplash_url, timeout=10)
        if resp.status_code == 200:
            data_json = resp.json()
            results = data_json.get("results", [])
            if results:
                # Use the first result or any from 'results'
                plant["imageUrl"] = results[0]["urls"].get("small", "")
            else:
                plant["imageUrl"] = ""
        else:
            plant["imageUrl"] = ""

    # 5) RETURN EVERYTHING (SATELLITE IMAGE, COORDS, RAW GEMINI TEXT, PARSED PLANTS)
    return jsonify(
        {
            "image": base64_image,  # The satellite image in base64
            "coordinates": coordinates,  # lat/lng
            "geminiRaw": raw_gemini_output,  # The original text from Gemini
            "plants": plants,  # The parsed array of 3 plant objects
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5200)
