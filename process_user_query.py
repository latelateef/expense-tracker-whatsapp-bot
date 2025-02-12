import json
import logging
from queries import add_expense, update_limit, view_limit, help, miscellaneous
from gemini import classify_message
from retrieve_expenses import retrieve_expense
from send_message import send_confirmation_message


logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='a')
logger = logging.getLogger(__name__)

# Function to process the user's query
def process_user_query(user_message, user_phone):
    """
    Processes the user's message by classifying it and triggering the appropriate function.
    """
    try:
        # Get classification result from AI model
        res = classify_message(user_message)
        res = json.loads(res)
        # print(res) # TODO: Remove this line

        # Route to appropriate function based on classification result
        if res.get("retrieve_expense"):
            return retrieve_expense(user_phone, user_message)
        elif res.get("add_expense"):
            return add_expense(user_phone, res)
        elif res.get("update_limit"):
            return update_limit(user_phone, res)
        elif res.get("view_limit"):
            return view_limit(user_phone)
        elif res.get("delete_all_expenses"):
            return send_confirmation_message(user_phone, "expense_deletion")
        elif res.get("delete_account"):
            return send_confirmation_message(user_phone, "account_deletion")
        elif res.get("help"):
            return help()
        else:
            return miscellaneous()  # If the query is not recognized, return a generic response.

    except Exception as e:
        logger.error(f"Unexpected error in process_user_query(): {str(e)}")
        return "An unexpected issue occurred. Please try again later."
