# app/modules/crop/routes.py
from fastapi import APIRouter, Query, HTTPException, status
from datetime import datetime

from modules.crop.schemas import RecommendationResponse
from modules.crop.services import get_crop_recommendations_from_gemini

# Assuming we have a service to simulate sensor data
from modules.sensor_data.services import get_simulated_sensor_data

router = APIRouter()

@router.get("/recommend/", response_model=RecommendationResponse)
async def recommend_crops(
    soil_type: str = Query(..., description="The classified soil type (e.g., Loamy Soil)."),
    season: str = Query(..., description="The current season (e.g., Rainy, Dry)."),
    zone: str = Query(..., description="The agro-ecological zone (e.g., Zone I, Zone II)."),
    latitude: float = Query(..., description="Latitude of the farm location."),
    longitude: float = Query(..., description="Longitude of the farm location."),
):
    """
    Recommends suitable crops based on general conditions and simulated real-time
    sensor data from a specific farm location using the Gemini AI model.
    """
    try:
        # Step 1: Simulate the sensor data for the given location
        sensor_data = get_simulated_sensor_data(latitude, longitude)

        # Step 2: Pass all parameters to the Gemini recommendation service
        recommendations_list = await get_crop_recommendations_from_gemini(
            soil_type=soil_type,
            season=season,
            zone=zone,
            latitude=sensor_data.latitude,
            longitude=sensor_data.longitude,
            soil_moisture=sensor_data.soil_moisture,
            soil_temperature=sensor_data.soil_temperature,
            electrical_conductivity=sensor_data.electrical_conductivity,
            soil_ph=sensor_data.soil_ph,
            relative_humidity=sensor_data.relative_humidity,
            solar_radiation=sensor_data.solar_radiation,
        )

        return RecommendationResponse(
            recommendations=recommendations_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during crop recommendation: {e}"
        )