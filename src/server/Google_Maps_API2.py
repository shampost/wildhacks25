from flask import Flask, request, jsonify
import requests
import urllib.parse
import base64

app = Flask(__name__)

# Replace with your valid Google Maps API key
API_KEY = ""

@app.route('/get-satellite-image', methods=['POST'])
def get_satellite_image():
    data = request.get_json()
    if not data or 'address' not in data:
        return jsonify({"error": "No address provided", "debug": "Missing address in request"}), 400

    address = data['address']
    encoded_address = urllib.parse.quote(address)
    
    # Use Google Geocoding API to get coordinates
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}"
    geocode_response = requests.get(geocode_url)
    geocode_data = geocode_response.json()
    
    if geocode_data['status'] != 'OK' or not geocode_data['results']:
        return jsonify({"error": "Unable to geocode address", "debug": geocode_data}), 400
    
    location = geocode_data['results'][0]['geometry']['location']
    lat, lng = location['lat'], location['lng']
    coordinates = {"lat": lat, "lng": lng}
    
    # Construct the URL for the Google Static Maps API (satellite view, 800x800)
    static_map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={encoded_address}&zoom=18&size=800x800&maptype=satellite&key={API_KEY}"
    )
    
    image_response = requests.get(static_map_url)
    if image_response.status_code != 200:
        return jsonify({"error": "Failed to fetch satellite image", "debug": image_response.text}), 500
    
    image_data = image_response.content
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    return jsonify({"image": base64_image, "coordinates": coordinates})

if __name__ == '__main__':
    app.run(debug=True, port=5200)