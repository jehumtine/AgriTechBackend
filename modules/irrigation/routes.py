# app/modules/irrigation/routes.py
from fastapi import APIRouter, HTTPException, status, Body, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from modules.irrigation.schemas import IrrigationScheduleRequest, IrrigationScheduleResponse
from modules.irrigation.irrigation_services import get_irrigation_schedule_from_gemini
from core.dependencies import get_current_user, get_db
from modules.auth.models import User

router = APIRouter()


@router.post("/schedule/", response_model=IrrigationScheduleResponse)
async def generate_irrigation_schedule(
        request: IrrigationScheduleRequest = Body(
            ...,
            description="Parameters for generating an irrigation schedule. Sensor data and weather forecasts are fetched/simulated internally."
        ),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Generates an irrigation schedule for a specified crop based on farm conditions,
    simulated real-time sensor data, and actual weather forecasts using the Gemini AI model.
    """
    # ... (code for farm_id validation) ...

    try:
        # Pass the db session to the service function
        schedule_details = await get_irrigation_schedule_from_gemini(request_data=request, db=db)

        return IrrigationScheduleResponse(
            crop_name=request.crop_name,
            schedule=schedule_details,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during irrigation schedule generation: {e}"
        )