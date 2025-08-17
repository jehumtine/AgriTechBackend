# app/modules/crop/routes.py
from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from datetime import datetime

from modules.crop.schemas import RecommendationRequest, RecommendationResponse
from modules.crop.services import get_crop_recommendations_from_gemini
from core.dependencies import get_current_user, get_db
from modules.auth.models import User

router = APIRouter()


@router.post("/recommend/", response_model=RecommendationResponse)
async def get_crop_recommendation_endpoint(
        request: RecommendationRequest = Body(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Generates a list of crop recommendations for a specific farm location.
    """
    # Verify the farm_id in the request belongs to the current user
    if not any(farm.id == request.farm_id for farm in current_user.farms):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this farm"
        )

    try:
        recommendations_list = await get_crop_recommendations_from_gemini(
            request_data=request,
            db=db
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