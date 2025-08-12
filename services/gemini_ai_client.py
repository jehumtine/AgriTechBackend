import google.generativeai as genai
from core.config import settings
from PIL import Image
from typing import Optional, Tuple, Dict, Any

# Configure the Google Generative AI with your API key
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Use the vision model for image input
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    gemini_model = None # Set to None if configuration fails


def get_gemini_model_for_text():
    """
    Returns a configured Gemini model for text-only generation.
    """
    return gemini_model



async def analyze_image_with_gemini(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Sends an image to the Gemini API with a prompt to identify soil type.
    """
    if gemini_model is None:
        print("Gemini model not initialized. Skipping API call.")
        return None

    try:
        img = Image.open(image_path).convert("RGB")

        # Craft a precise prompt for soil classification
        prompt_parts = [
            "Analyze the following image of soil. Identify the primary soil type (e.g., Sandy Soil, Clayey Soil, Loamy Soil, Silt Soil, Peat Soil, Black Soil, Red Soil, Alluvial Soil). "
            "Also, provide a confidence level for your classification on a scale of 0 to 100. "
            "Respond in a JSON format with 'soil_type' and 'confidence' keys. "
            "DO NOT FORMAT WITH ```json Dont do that. Just RETURN {} json"
            "Example: {\"soil_type\": \"Loamy Soil\", \"confidence\": 90}"
            , img
        ]

        # Use the generate_content method for multimodal input
        # Setting stream=True can be useful for long responses, but for JSON, False is fine.
        response = await gemini_model.generate_content_async(prompt_parts) # Await the async call

        # Access the text from the response
        response_text = response.text
        print(f"Gemini raw response: {response_text}")

        # Parse the JSON response
        import json
        try:
            parsed_response = json.loads(response_text)
            return parsed_response
        except json.JSONDecodeError:
            print(f"Gemini response was not valid JSON: {response_text}")
            return {"soil_type": "Parse Error", "confidence": 0}

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

if __name__ == "__main__":
    # Example usage for testing the client directly
    import asyncio
    import os
    import random

    # Create a dummy image file for testing
    dummy_image_path = "dummy_soil_image_for_inference.jpg"
    try:
        async def test_gemini_client():
            result = await analyze_image_with_gemini(dummy_image_path)
            if result:
                print(f"Gemini Predicted Soil Type: {result.get('soil_type')} with Confidence: {result.get('confidence')}")
            else:
                print("Gemini API call failed.")

        asyncio.run(test_gemini_client())
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)