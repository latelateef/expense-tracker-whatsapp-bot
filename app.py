from flask import Flask, request, jsonify
from flask_migrate import Migrate
import json
from models import db, init_app, User
from process_user_query import process_user_query
from send_message import send_response_message
from check_confirmation import check_confirmation_response
import logging


logging.basicConfig(level=logging.ERROR, filename="app.log", filemode="a")
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"

# Initialize the database
init_app(app)
migrate = Migrate(app, db)


# Define the route for the WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    try:
        parsed_msg = request.form
        from_number = parsed_msg.get("From")
        incoming_msg = parsed_msg.get("Body", "").strip()

        response_message = ""

        # Check if the user is new
        user = User.get_user_by_phone(from_number)
        if not user:
            user = User.create_user(from_number, 5000.0)
            with open("texts/messages.json", "r", encoding="utf-8") as file:
                messages = json.load(file)
            welcome_message = messages.get("welcome_message").format(
                limit_amount=user.limit_amount
            )
            response_message += welcome_message

        # Check if user is in the process of confirming the deletion
        if user.state:
            response_message = check_confirmation_response(
                from_number, user.state, incoming_msg
            )
        else: # Process the user's query
            response_message += process_user_query(incoming_msg, from_number)

        # Send the response message
        if not response_message:
            response_message = "An error occurred while processing your request. Please try again later."
        send_response_message(from_number, response_message)
        # print(response_message) # TODO: Remove this line
        return jsonify({"message": "Message sent successfully."}, 200)

    except Exception as e:
        logger.error(f"Internal Server Error {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}, 500)


if __name__ == "__main__":
    app.run(debug=True)
