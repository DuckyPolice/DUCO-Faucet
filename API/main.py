import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

COOLDOWN_DURATION = 15 * 60  # 15 minutes
MESSAGE = "Stormsurge Faucet here!!"
AMOUNT = 10
PASSWORD = ""
HOST_USERNAME = "DuckyPolice"
RECAPTCHA_SECRET_KEY = "6Lemf8spAAAAAObbAXy_xQtGiMPKyd-Tnulu9ASo"

user_cooldowns = {}

def is_user_blacklisted(username):
    try:
        with open("blacklist.txt", "r") as file:
            blacklist = [line.strip().lower() for line in file.readlines()]
            return any(entry in username.lower() for entry in blacklist)
    except Exception as e:
        print(f"Failed to check blacklist for user {username}: {e}")
        return False

@app.route("/transaction/<user_id>", methods=["GET"])
def transaction(user_id):
    current_time = datetime.now()
    
    request_data = {
        "user_id": user_id,
        "recaptcha_token": request.args.get("recaptchaToken"),
        "client_ip": request.remote_addr,
        "user_agent": request.user_agent.string
    }
    print("Received API Request Data:")
    print(json.dumps(request_data, indent=4))

    recaptcha_token = request_data["recaptcha_token"]
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": recaptcha_token
    })
    recaptcha_data = response.json()
    if not recaptcha_data["success"]:
        return jsonify({"success": False, "message": "reCAPTCHA verification failed"}), 400

    if is_user_blacklisted(user_id):
        print(f"{user_id} was blacklisted so the request was blocked.")
        return "User is blacklisted. Transaction not allowed.", 403

    last_request_time = user_cooldowns.get(user_id, datetime.min)
    if (current_time - last_request_time).seconds < COOLDOWN_DURATION:
        cooldown_remaining = max(0, COOLDOWN_DURATION - (current_time - last_request_time).seconds)
        print(f"Cooldown: User {user_id} is on cooldown. Remaining time: {cooldown_remaining} seconds.")
        return f"Cooldown: Please wait before initiating another request for user {user_id}. Remaining time: {cooldown_remaining} seconds.", 429

    try:
        response = requests.get(f"https://server.duinocoin.com/transaction?username={HOST_USERNAME}&password={PASSWORD}&recipient={user_id}&amount={AMOUNT}&memo={MESSAGE}")
        if response.status_code == 200:
            user_cooldowns[user_id] = current_time
            print(f"Successful transaction for user {user_id}.")
            return "Successful transaction!", 200
        else:
            print(f"Unsuccessful transaction for user {user_id}.")
            user_cooldowns[user_id] = current_time
            return "Unsuccessful transaction.", 400

    except requests.exceptions.RequestException as e:
        print(f"Exception: {e}. Unsuccessful transaction for user {user_id}.")
        user_cooldowns[user_id] = current_time
        return "Unsuccessful transaction.", 500

if __name__ == "__main__":
    app.run(port=80)
