from twilio.rest import Client
from dotenv import load_dotenv
import os
from user_state import set_user_state
import json

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
def send_response_message(user_phone, response_message):
    message = client.messages.create(
        body=response_message, from_=TWILIO_PHONE_NUMBER, to=user_phone
    )
    return message


def send_confirmation_message(user_phone, state):
    # Send the confirmation message with reply for "Yes" and "No"
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    confirmation_msg = messages["confirmation_message"]
    if state == "expense_deletion":
        confirmation_msg = confirmation_msg.format(state="expenses")
    elif state == "account_deletion":
        confirmation_msg = confirmation_msg.format(state="account")

    # Set the user state for deletion confirmation
    set_user_state(user_phone, state)

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
    #     content_sid="HX9fe7e687ab935c63ccb68c3745661a4d"
    # )
    return confirmation_msg
