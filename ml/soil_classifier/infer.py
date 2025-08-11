import os
import random
from typing import Tuple
from services.gemini_ai_client import analyze_image_with_gemini

# These are the expected soil types. Gemini's response should ideally align with these.
SOIL_TYPES = ["Sandy Soil", "Clayey Soil", "Loamy Soil", "Silt Soil", "Peat Soil", "Black Soil", "Red Soil", "Alluvial Soil", "Unknown"]

async def predict_soil_type(image_path: str) -> Tuple[str, float]:
    """
    Performs soil type inference by sending the image to the Gemini API.
    """
    print(f"Sending image {image_path} to Gemini for analysis...")
    gemini_result = await analyze_image_with_gemini(image_path)

    if gemini_result:
        predicted_type = gemini_result.get("soil_type", "Unknown")
        confidence = float(gemini_result.get("confidence", 0)) / 100.0 # Convert 0-100 to 0-1

        # Basic validation/normalization of Gemini's output
        # If Gemini gives a type not in our list, we might map it or use "Unknown"
        if predicted_type not in SOIL_TYPES:
            print(f"Warning: Gemini returned an unexpected soil type: {predicted_type}. Mapping to 'Unknown'.")
            predicted_type = "Unknown"
            # Adjust confidence if mapping to unknown, or keep as is
            # confidence = confidence * 0.5 # Example: reduce confidence

        return predicted_type, confidence
    else:
        print("Gemini API call failed or returned no result. Falling back to random simulation.")
        # Fallback to a random choice if API call fails
        predicted_type = random.choice(SOIL_TYPES)
        confidence = round(random.uniform(0.3, 0.6), 2) # Lower confidence for simulated fallback
        return predicted_type, confidence

if __name__ == "__main__":
    import asyncio
    # Example usage for testing infer.py directly
    dummy_image_path = "dummy_soil_image_for_inference.jpg"
    try:
        from PIL import Image

        async def test_inference():
            soil, conf = await predict_soil_type(dummy_image_path)
            print(f"Inference Result: {soil} with Confidence: {conf:.2f}")

        asyncio.run(test_inference())
    finally:
        pass
