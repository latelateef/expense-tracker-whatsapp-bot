from twilio.rest import Client
from dotenv import load_dotenv
import os
import json
from models import User
import logging

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

logging.basicConfig(level=logging.ERROR, filename="app.log", filemode="a")
logger = logging.getLogger(__name__)

try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {str(e)}")
    raise Exception("Failed to initialize Twilio client. Please check the Twilio account SID and AUTH Token.")

def send_response_message(user_phone, response_message):
    try:
        message = client.messages.create(
            body=response_message, from_=TWILIO_PHONE_NUMBER, to=user_phone
        )
        return message
    except Exception as e:
        logger.error(f"Error sending response message: {str(e)}")
        return None

def send_confirmation_message(user_phone, state):
    try:
        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        confirmation_msg = messages.get("confirmation_message", "Are you sure you want to proceed?")
        if state == "expense_deletion":
            confirmation_msg = confirmation_msg.format(state="expenses")
        elif state == "account_deletion":
            confirmation_msg = confirmation_msg.format(state="account")

        User.set_user_state(user_phone, state)
    except Exception as e:
        logger.error(f"Error sending confirmation message: {str(e)}")
        return None

    # Define the quick reply buttons
    # actions = [
    #     {
    #         "type": "quick_reply",
    #         "title": "Yes",
    #         "id": "yes"
    #     },
    #     {
    #         "type": "quick_reply",
    #         "title": "No",
    #         "id": "no"
    #     }
    # ]

    # # Create the content
    # content = {
    #     "body": confirmation_msg,
    #     "actions": actions
    # }

    # Send the message
    # message = client.messages.create(
    #     from_=TWILIO_PHONE_NUMBER,
    #     to=user_phone,
    #     content_variables=content,
    #     content_sid=os.getenv("TWILIO_CONTENT_TEMPLATE_SID")
    # )

    return confirmation_msg

