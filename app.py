from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from twilio.rest import Client
from flask_migrate import Migrate
from models import db, init_app, User, Expense


load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
print(TWILIO_PHONE_NUMBER)
print(TWILIO_ACCOUNT_SID)
print(TWILIO_AUTH_TOKEN)

init_app(app)
migrate = Migrate(app, db)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    parsed_msg = request.form
    from_number = parsed_msg.get("From")
    incoming_msg = parsed_msg.get("Body", "").strip()
    print(incoming_msg)
    if not incoming_msg:
        return jsonify({"message": "Please provide a message."}, 400)

    response_message = f"Hello! You sent the message: {incoming_msg}"
    message = client.messages.create(
        body=response_message, from_=TWILIO_PHONE_NUMBER, to=from_number
    )
    return jsonify({"message": "✅ Message sent successfully."}, 200)


if __name__ == "__main__":
    app.run(debug=True)