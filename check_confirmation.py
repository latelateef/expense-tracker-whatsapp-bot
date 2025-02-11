from queries import delete_all_expenses, delete_account
from user_state import reset_user_state
import json

def check_confirmation_response(user_phone, user_state, response):
    response_message = ""
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    if user_state == "expense_deletion":
        if response.lower().startswith("yes"):
            response_message = delete_all_expenses(user_phone)
        elif response.lower().startswith("no"):
            response_message = messages["deletion_canceled"]

        reset_user_state(user_phone)
    elif user_state == "account_deletion":
        if response.lower().startswith("yes"):
            response_message = delete_account(user_phone)
        elif response.lower().startswith("no"):
            response_message = messages["deletion_canceled"]

        reset_user_state(user_phone)

    return response_message