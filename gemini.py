import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='a')
logger = logging.getLogger(__name__)

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
except Exception as e:
    logger.error(f"Error configuring Gemini AI: {str(e)}")
    raise Exception("Error configuring Gemini AI. Please check the API key.")

def classify_message(message):
    """
    Classifies a given message using the Gemini AI model.
    """
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), "texts/classification_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read()
        prompt = prompt.replace("{message}", message)

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        # Extract the JSON content from the response
        content = response.text.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return content

    except Exception as e:
        logger.error(f"Unexpected error in classify_message: {str(e)}")
        return "Error: An unexpected issue occurred. Please try again later."
