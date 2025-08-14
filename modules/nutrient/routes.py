from fastapi import APIRouter, HTTPException, status, Body
from datetime import datetime

from modules.nutrient.schemas import NutrientPlanRequest, NutrientPlanResponse, InternalNutrientPlanRequest
from modules.nutrient.services import get_nutrient_plan_from_gemini

# Assuming we have a service to simulate sensor data
from modules.sensor_data.services import get_simulated_sensor_data

router = APIRouter()

@router.post("/plan/", response_model=NutrientPlanResponse)
async def generate_nutrient_plan(
    request: NutrientPlanRequest = Body(
        ...,
        description="Parameters for generating a nutrient plan. Sensor data is simulated for the given location."
    )
):
    """
    Generates a detailed nutrient plan for a specified crop based on farm conditions
    and simulated real-time sensor data using the Gemini AI model.
    """
    try:
        # Step 1: Simulate the sensor data for the given location
        simulated_data = get_simulated_sensor_data(request.latitude, request.longitude)

        # Step 2: Create a complete internal request object with all data
        internal_request = InternalNutrientPlanRequest(
            crop_name=request.crop_name,
            soil_type=request.soil_type,
            season=request.season,
            zone=request.zone,
            latitude=request.latitude,
            longitude=request.longitude,
            soil_moisture=simulated_data.soil_moisture,
            soil_temperature=simulated_data.soil_temperature,
            electrical_conductivity=simulated_data.electrical_conductivity,
            soil_ph=simulated_data.soil_ph,
            relative_humidity=simulated_data.relative_humidity,
            solar_radiation=simulated_data.solar_radiation,
        )

        # Step 3: Pass the entire internal request object to the Gemini service
        plan_details = await get_nutrient_plan_from_gemini(request_data=internal_request)

        return NutrientPlanResponse(
            crop_name=internal_request.crop_name,
            plan_details=plan_details,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during nutrient plan generation: {e}"
        )