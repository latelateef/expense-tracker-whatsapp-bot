import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def classify_message(message):
    """
    Uses Gemini AI to determine if a message is an expense entry or a query, or update limit.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "sentiment_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt = file.read()

    # Replace placeholder with actual message
    prompt = prompt.replace("{message}", message)

    # Initialize the model
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Generate response
    response = model.generate_content(prompt)
    if response and hasattr(response, "text"):
            content = response.text
            content = content.replace("```json", "").replace("```", "").strip()
            return content
    else:
            return "Error: No content generated."


