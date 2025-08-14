from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from datetime import datetime

from modules.nitrate.schemas import NitrateStatusResponse, NitrateAlert
from modules.nitrate.services import get_nitrate_status_from_gemini

router = APIRouter()

@router.get("/status/", response_model=NitrateStatusResponse)
async def get_nitrate_status(
    latitude: float = Query(..., description="Latitude of the farm location."),
    longitude: float = Query(..., description="Longitude of the farm location."),
    farm_id: Optional[int] = Query(None, description="The ID of the farm (optional).")
):
    """
    Retrieves the current nitrate level and a risk assessment for a specific farm
    location using a simulation engine powered by the Gemini AI model.
    """
    try:
        nitrate_status = await get_nitrate_status_from_gemini(
            latitude=latitude,
            longitude=longitude,
            farm_id=farm_id
        )

        return nitrate_status

    except Exception as e:
        # We catch any potential errors from the service and return a 500 status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during nitrate status retrieval: {e}"
        )