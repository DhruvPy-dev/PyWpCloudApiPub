from flask import Flask, request, jsonify
import os
import requests
import json


app = Flask(__name__)

# Access token for your app
# (copy token from DevX getting started page
# and save it as environment variable into the .env file)

token = os.environ["WHATSAPP_TOKEN"]

# Verify token for webhook verification
verify_token = os.environ["VERIFY_TOKEN"]

@app.route("/webhook", methods=["POST"])
def webhook():
    # Parse the request body from the POST
    body = request.json

    # Check the Incoming webhook message
    print(json.dumps(request.json, indent=2))

    if request.json.get("object"):
        if (
            request.json.get("entry")
            and request.json["entry"][0].get("changes")
            and request.json["entry"][0]["changes"][0].get("value").get("messages")
        ):
            phone_number_id = request.json["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
            from_number = request.json["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            msg_body = request.json["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

            # Send reply back to sender using WhatsApp API
            url = (
                "https://graph.facebook.com/v12.0/{}/messages?access_token={}".format(
                    phone_number_id, token
                )
            )
            data = {"messaging_product": "whatsapp", "to": from_number, "text": {"body": "Ack: " + msg_body}}
            headers = {"Content-Type": "application/json"}
            requests.post(url, json=data, headers=headers)

        return jsonify({"status": "success"}), 200
    else:
        # Return a '404 Not Found' if event is not from a WhatsApp API
        return jsonify({"status": "not found"}), 404

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return jsonify({"status": "success"}), 200, challenge
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            return jsonify({"status": "forbidden"}), 403

if __name__ == ("__main__"):
    app.run()
