# app/modules/nutrient/routes.py
from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session  # Import Session
from datetime import datetime

from modules.nutrient.schemas import NutrientPlanRequest, NutrientPlanResponse
from modules.nutrient.services import get_nutrient_plan_from_gemini
from core.dependencies import get_current_user, get_db  # Import authentication and DB dependency
from modules.auth.models import User  # Import User model for type hinting

router = APIRouter()


@router.post("/plan/", response_model=NutrientPlanResponse)
async def generate_nutrient_plan_endpoint(
        request: NutrientPlanRequest = Body(
            ...,
            description="Parameters for generating a nutrient plan. Sensor data is simulated internally."
        ),
        current_user: User = Depends(get_current_user),  # Secure this endpoint
        db: Session = Depends(get_db)  # Inject database session
):
    """
    Generates a detailed nutrient plan for a specified crop based on farm conditions
    and simulated real-time sensor data using the Gemini AI model. The plan is saved.
    """
    # Verify the farm_id in the request belongs to the current user
    if not any(farm.id == request.farm_id for farm in current_user.farms):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )

    try:
        # Pass the request data and the database session to the service
        plan_details_list = await get_nutrient_plan_from_gemini(
            request_data=request,
            db=db
        )

        return NutrientPlanResponse(
            crop_name=request.crop_name,  # Use crop_name from the request
            plan_details=plan_details_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        # Proper error handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during nutrient plan generation: {e}"
        )