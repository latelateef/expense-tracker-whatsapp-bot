from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handles incoming WhatsApp messages from Twilio."""
    incoming_message = request.form.get("Body")
    sender = request.form.get("From")

    print(f"Received message from {sender}: {incoming_message}")

    response = MessagingResponse()
    response.message(f"Hello! You said: {incoming_message}")

    return str(response)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
