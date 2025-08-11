import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.soil.schemas import SoilAnalysisResponse
from modules.soil.services import UPLOAD_DIR, analyze_soil_image_only

# Create an APIRouter instance
router = APIRouter()

@router.post("/analyze-image/", response_model=SoilAnalysisResponse)
async def analyze_soil_image_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a soil image, sends it to the Gemini API for analysis, and
    returns the predicted soil type.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image."
        )

    # Generate a unique filename and save the uploaded image temporarily
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = UPLOAD_DIR / unique_filename

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the service function to perform the analysis
        soil_analysis_result = await analyze_soil_image_only(db, str(file_location))

        return SoilAnalysisResponse(
            id=soil_analysis_result.id,
            image_filename=soil_analysis_result.image_filename,
            predicted_soil_type=soil_analysis_result.predicted_soil_type,
            confidence=soil_analysis_result.confidence,
            analysis_timestamp=soil_analysis_result.analysis_timestamp
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image for soil analysis: {e}"
        )
    finally:
        # Ensure the temporary file is deleted after processing
        if os.path.exists(file_location):
            os.remove(file_location)