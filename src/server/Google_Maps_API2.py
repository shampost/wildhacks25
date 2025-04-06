from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import requests
import urllib.parse
import base64

app = Flask(__name__)
# Allow requests from any origin by explicitly setting origins to "*"
CORS(app, resources={r"/*": {"origins": "*"}})

# Replace with your valid Google Maps API key
API_KEY = ""

@app.route("/get-satellite-image", methods=["POST"])
def get_satellite_image():
    data = request.get_json()
    if not data or "address" not in data:
        return (
            jsonify(
                {"error": "No address provided", "debug": "Missing address in request"}
            ),
            400,
        )

    address = data["address"]
    encoded_address = urllib.parse.quote(address)

    # Use Google Geocoding API to get coordinates
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}"
    geocode_response = requests.get(geocode_url)
    geocode_data = geocode_response.json()

    if geocode_data["status"] != "OK" or not geocode_data["results"]:
        return (
            jsonify({"error": "Unable to geocode address", "debug": geocode_data}),
            400,
        )

    location = geocode_data["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]
    coordinates = {"lat": lat, "lng": lng}

    # Construct the URL for the Google Static Maps API (satellite view, 800x800)
    static_map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={encoded_address}&zoom=18&size=800x800&maptype=satellite&key={API_KEY}"
    )

    image_response = requests.get(static_map_url, timeout=10)
    if image_response.status_code != 200:
        return (
            jsonify(
                {
                    "error": "Failed to fetch satellite image",
                    "debug": image_response.text,
                }
            ),
            500,
        )

    image_data = image_response.content
    base64_image = base64.b64encode(image_data).decode("utf-8")

    # Use encoded_address in Gemini API call:
    client = genai.Client(api_key="")
    gemini_prompt = f"""You are an expert agronomist with deep knowledge of hyperlocal climate conditions. Given the region corresponding to the address: {address} (encoded as {encoded_address}), recommend exactly three plants or crops that are best suited for growth in that region. For each recommendation, include:
- 'plantName': The common name of the plant.
- 'scientificName': The scientific name of the plant.
- 'reason': A concise one-sentence explanation of why this plant is ideal for the region.
- 'careInstruction': A brief one-sentence plant care instruction.
Return only a valid JSON array of exactly three objects with the keys 'plantName', 'scientificName', 'reason', and 'careInstruction'. Do not include any additional text or commentary."""
    gemini_response = client.models.generate_content(
        model="gemini-2.0-flash", contents=gemini_prompt
    )

    # Print Gemini's output to the console for debugging
    print("Gemini response:", gemini_response.text)

    # Return the JSON response with the Gemini output included.
    return jsonify(
        {
            "image": base64_image,
            "coordinates": coordinates,
            "gemini": gemini_response.text,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5200)
