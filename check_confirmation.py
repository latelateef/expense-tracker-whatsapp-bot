import json
import logging
from queries import delete_all_expenses, delete_account
from models import User

logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='a')
logger = logging.getLogger(__name__)

def check_confirmation_response(user_phone, user_state, response):
    """
    Handles confirmation response for expense/account deletion.
    """
    response_message = ""

    # Load messages from JSON file
    try:
        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        if user_state == "expense_deletion":
            if response.lower().startswith("yes"):
                response_message = delete_all_expenses(user_phone)
                User.reset_user_state(user_phone)
            elif response.lower().startswith("no"):
                response_message = messages.get("deletion_canceled", "Deletion canceled.")
                User.reset_user_state(user_phone)
            else:
                response_message = "Invalid message. Please try again."


        elif user_state == "account_deletion":
            if response.lower().startswith("yes"):
                response_message = delete_account(user_phone)
            elif response.lower().startswith("no"):
                response_message = messages.get("deletion_canceled", "Deletion canceled.")
                User.reset_user_state(user_phone)
            else:
                response_message = "Invalid message. Please try again."

    except Exception as e:
        logger.error(f"Error processing confirmation response: {str(e)}")
        response_message = "An unexpected error occurred. Please try again later."

    return response_message
