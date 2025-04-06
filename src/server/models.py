from pydantic import BaseModel
from typing import Optional

class PlantRecognitionRequest(BaseModel):
    image_data: str  # Base64-encoded image or image URL for now (simulate image upload)

class PlantInfo(BaseModel):
    name: str
    season: str
    description: str
    care: str
    scientific_name: Optional[str] = None
    origin: Optional[str] = None
    soil_type: Optional[str] = None
    sunlight: Optional[str] = None
    watering: Optional[str] = None
    health_status: Optional[str] = None  

class PlantRecognitionResponse(BaseModel):
    success: bool
    plant: Optional[PlantInfo] = None
    message: Optional[str] = None
