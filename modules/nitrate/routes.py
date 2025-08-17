from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import Optional
from sqlalchemy.orm import Session

from modules.nitrate.schemas import NitrateStatusRequest, NitrateStatusResponse
from modules.nitrate.services import get_nitrate_status as get_nitrate_service
from core.dependencies import get_current_user, get_db
from modules.auth.models import User

router = APIRouter()


@router.get("/status/", response_model=NitrateStatusResponse)
async def get_nitrate_status_endpoint(
        latitude: float = Query(..., description="Latitude of the farm location."),
        longitude: float = Query(..., description="Longitude of the farm location."),
        farm_id: Optional[int] = Query(None, description="The ID of the farm (optional)."),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Retrieves the current nitrate level and a risk assessment for a specific farm
    location using a simulation engine powered by the Gemini AI model.
    """
    print("Entered get_nitrate_status_endpoint")

    # Security check: Ensure the farm_id belongs to the current user
    if not any(farm.id == farm_id for farm in current_user.farms):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )

    # Create a request object for the service layer
    request_data = NitrateStatusRequest(
        farm_id=farm_id,
        latitude=latitude,
        longitude=longitude
    )

    try:
        # Call the service function with the correct name and pass the database session
        nitrate_status = await get_nitrate_service(
            request_data=request_data,
            db=db
        )

        return nitrate_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during nitrate status retrieval: {e}"
        )