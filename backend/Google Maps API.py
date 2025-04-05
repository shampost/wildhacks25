#Back-End Development for Gardening Website
# WildHacks 2025 Los Stars
import requests
from dotenv import load_dotenv
import os
from PIL import Image
import io


#Loads API Key from.env file
load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def get_satellite_image(address, zoom=18, size="600x600"):
    
    #First Geocodes the Address to retrieve the coordinates
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={
    address}&key={API_KEY}"
    response = requests.get(geocode_url)
    data = response.json()

    if data ['status'] != 'OK':
        print(f"Geocoding failed: {data.get('error_message', 'Unknown error')}")
        return None

    location = data['results'][0]['geometry']['location']
    lat = location ['lat']
    lng = location ['lng']

    #Get the satellite image
    static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size={size}&maptype=satellite&key={API_KEY}"

    image_response = requests.get(static_map_url)
    if image_response.status_code == 200:

#Get the image response
        img_bytes = image_response.content
        Image.open(io.BytesIO(img_bytes)).show()
        
        return img_bytes
    else:
        print("Failed to download satellite image")
        return None
    
#Example Usage
if __name__ == "__main__":
    address = input("Enter an address: ")
    get_satellite_image(address.strip())
                                 
                                 
                        
