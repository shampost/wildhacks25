# Back-End Development for Gardening Website
# WildHacks 2025 Los Stars
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import base64
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Loads API Key from.env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def get_satellite_image(address, zoom=10, size="600x600"):
    # Fetch Satellite Image from Google maps API
    try:
        if not API_KEY:
            return {"error": "API key not configured"}

        # Geocode address
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
        geo_response = requests.get(geocode_url, timeout=10)
        geo_data = geo_response.json()

        if geo_data["status"] != "OK":
            return {
                "error": geo_data.get("error_message", "Geocoding failed"),
                "debug": geo_data,  # Includes full response
            }

        # Get Coordinates
        location = geo_data["results"][0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]

        # Get the satellite image
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size={size}&maptype=satellite&key={API_KEY}"

        map_response = requests.get(map_url, timeout=10)
        map_response.raise_for_status()

        return {"image": map_response.content, "coordinates": location}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@app.route("/get-satellite-image", methods=["POST"])
def handle_request():
    # Endpoint for front-end requests

    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        address = request.json.get("address")
        if not address:
            return jsonify({"error": "Address is required"}), 400

        # Get image data
        result = get_satellite_image(address)

        # Handle Errors
        if not result:
            return jsonify({"error": "No response from API"}), 500
        if "error" in result:
            return (
                jsonify({"error": result["error"], "debug": result.get("debug")}),
                400,
            )
        # Return successful response
        return jsonify(
            {
                "image": base64.b64encode(result["image"]).decode("utf-8"),
                "coordinates": result["coordinates"],
            }
        )
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.errorhandler(HTTPException)
def handle_exception(e):
    # JSON format for HTTP Errors
    return jsonify({"error": e.name, "message": e.description}), e.code


if __name__ == "__main__":
    if not API_KEY:
        print("WARNING: Google Maps API key not found in .env file")

    # Run with debug mode OFF for production testing
    app.run(host="0.0.0.0", port=5200, debug=False)
