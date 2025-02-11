from flask import Flask, request, jsonify
from flask_migrate import Migrate
import json
from models import db, init_app, User
from process_user_query import process_user_query
from send_message import send_response_message
from user_state import get_user_state
from check_confirmation import check_confirmation_response


# Initialize the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"

# Initialize the database
init_app(app)
migrate = Migrate(app, db)

# Define the route for the WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    parsed_msg = request.form
    from_number = parsed_msg.get("From")
    incoming_msg = parsed_msg.get("Body", "").strip()
    if not incoming_msg:
        return jsonify({"message": "Please provide a message."}, 400)

    response_message = """"""

    # Check if user is in the process of confirming the deletion
    user_state = get_user_state(from_number)
    if user_state:
        response_message = check_confirmation_response(from_number, user_state, incoming_msg)

    # If user is messaging normally i.e. not in the process of confirming the deletion
    else:
        # Check if the user is new
        user = db.session.query(User).filter_by(user_phone=from_number).first()
        # If the user is new, add them to the database and send a welcome message
        if not user:
            user = User(user_phone=from_number, limit_amount=5000)
            db.session.add(user)
            db.session.commit()

            # Load welcome message from JSON file
            with open("messages.json", "r", encoding="utf-8") as file:
                messages = json.load(file)
            welcome_message = messages["welcome_message"].format(limit_amount=user.limit_amount)
            response_message += welcome_message

        # Process the user's query
        response_message += process_user_query(
            incoming_msg, from_number
        )

        print(response_message)

    # Send the response message
    message = send_response_message(from_number, response_message)
    return jsonify({"message": "Message sent successfully."}, 200)

if __name__ == "__main__":
    app.run(debug=True)
