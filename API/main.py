from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cooldown duration in seconds
COOLDOWN_DURATION = (15 * 60)  # 15 minutes
MESSAGE = "<Your memo here>"
AMOUNT = 10  # you can change this to whatever you want
PASSWORD = "<The host account's password>"
HOST_USERNAME = "<Username that will be sending the duco>"
RECAPTCHA_SECRET_KEY = "<Your reCAPTCHA secret key>"

# Dictionary to store the last request timestamp for each user ID
user_cooldowns = {}

def is_user_verified(username):
    try:
        response = requests.get(f"https://server.duinocoin.com/users/{username}")
        response.raise_for_status()
        user_data = response.json().get("result", {}).get("balance", {})
        verified_status = user_data.get("verified", "").lower()
        print(f"Verification status for user {username}: {verified_status}")
        return verified_status == "yes"
    except requests.exceptions.RequestException as e:
        print(f"Failed to verify user {username}: {e}")
        return False

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

    # Verify ReCAPTCHA token
    recaptcha_token = request.args.get("recaptchaToken")
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": recaptcha_token
    })
    recaptcha_data = response.json()
    if not recaptcha_data["success"]:
        return jsonify({"success": False, "message": "reCAPTCHA verification failed"}), 400

    # Check if user is on the blacklist
    if is_user_blacklisted(user_id):
        print(f"{user_id} was blacklisted so the request was blocked.")
        return "User is blacklisted. Transaction not allowed.", 403

    # Check if user is verified
    if not is_user_verified(user_id):
        return "We're sorry, but unverified accounts are not allowed. Please verify your DUCO account.", 403

    # Check if user ID is on cooldown
    last_request_time = user_cooldowns.get(user_id, datetime.min)
    if (current_time - last_request_time).seconds < COOLDOWN_DURATION:
        cooldown_remaining = max(0, COOLDOWN_DURATION - (current_time - last_request_time).seconds)
        print(f"Cooldown: User {user_id} is on cooldown. Remaining time: {cooldown_remaining} seconds.")
        return f"Cooldown: Please wait before initiating another request for user {user_id}. Remaining time: {cooldown_remaining} seconds.", 429

    try:
        # Perform the transaction using requests
        response = requests.get(f"https://server.duinocoin.com/transaction?username={HOST_USERNAME}&password={PASSWORD}&recipient={user_id}&amount={AMOUNT}&memo={MESSAGE}")

        if response.status_code == 200:
            # Update the cooldown for the user ID
            user_cooldowns[user_id] = current_time
            print(f"Successful transaction for user {user_id}.")
            return "Successful transaction!", 200
        else:
            print(f"Unsuccessful transaction for user {user_id}.")
            # Even if unsuccessful, update the cooldown
            user_cooldowns[user_id] = current_time
            return "Unsuccessful transaction.", 400

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        print(f"Exception: {e}. Unsuccessful transaction for user {user_id}.")
        # Even if unsuccessful, update the cooldown
        user_cooldowns[user_id] = current_time
        return "Unsuccessful transaction.", 500

if __name__ == "__main__":
    app.run(port=7457)  # Change port as needed
