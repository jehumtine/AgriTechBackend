import os
from pathlib import Path
from sqlalchemy.orm import Session

from ml.soil_classifier.infer import predict_soil_type
from modules.soil.model import SoilAnalysis

# Define a temporary directory to save uploaded images
# This directory will be created if it doesn't exist
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def analyze_soil_image_only(db: Session, image_file_path: str) -> SoilAnalysis:
    """
    Analyzes a soil image using the Gemini API and stores the result.
    This service function focuses purely on image-based analysis.
    """
    if not image_file_path or not os.path.exists(image_file_path):
        # Handle case where no image path is provided or file doesn't exist
        # In a real app, you might raise an HTTPException here or return a specific error.
        print("Error: No image file path provided or file does not exist.")
        # Return a dummy or error SoilAnalysis object for consistency
        return SoilAnalysis(
            image_filename="N/A",
            predicted_soil_type="Error: No Image",
            confidence=0.0
        )

    print(f"Starting analysis for image: {image_file_path}")
    # Call the ML inference function, which now uses the Gemini API
    predicted_type, confidence = await predict_soil_type(image_file_path)

    # You can add simple post-processing or logging here if needed
    print(f"Analysis complete. Predicted: {predicted_type}, Confidence: {confidence:.2f}")

    # Save analysis result to the database
    db_soil_analysis = SoilAnalysis(
        image_filename=os.path.basename(image_file_path),
        predicted_soil_type=predicted_type,
        confidence=confidence
    )
    db.add(db_soil_analysis)
    db.commit()
    db.refresh(db_soil_analysis)

    return db_soil_analysis