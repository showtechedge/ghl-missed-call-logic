import logging
import datetime
import os
from flask import Flask, request, jsonify

# --- 1. CONFIGURATION ---
app = Flask(__name__) # Initialize the Flask App

# Define Business Hours (Lagos Time: UTC+1)
OPEN_HOUR = 9   # 9 AM
CLOSE_HOUR = 17 # 5 PM

VIP_NUMBERS = [
    "+2348000000000", 
    "+2349000000000",
    "Olushola"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_business_hours(timestamp_utc):
    utc_time = datetime.datetime.fromtimestamp(timestamp_utc, datetime.timezone.utc)
    lagos_time = utc_time + datetime.timedelta(hours=1)
    return OPEN_HOUR <= lagos_time.hour < CLOSE_HOUR

# --- 2. THE WEBHOOK ROUTE ---
# This listens for POST requests sent to http://your-ip/webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    # Get the JSON data sent by the "Sender" (Simulated GHL)
    payload = request.json
    
    if not payload:
        return jsonify({"error": "No data received"}), 400

    # Extract Data
    contact_phone = payload.get('phone', payload.get('contact', {}).get('phone'))
    contact_name = payload.get('firstName', payload.get('contact', {}).get('firstName', 'Valued Client'))
    
    # Use current time if no timestamp provided
    current_utc_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
    timestamp = payload.get('timestamp', current_utc_timestamp)

    logging.info(f"Received Webhook for: {contact_name}")

    # Logic: VIP Check
    if contact_phone in VIP_NUMBERS or contact_name in VIP_NUMBERS:
        message = f"Hello {contact_name}, VIP Alert! Alerting personal assistant."
        logging.info(f"DECISION: VIP -> {message}")
        return jsonify({"status": "success", "action": "sent_vip_sms", "message": message})

    # Logic: Business Hours Check
    if check_business_hours(timestamp):
        message = f"Hi {contact_name}, calling you back within the hour!"
        logging.info(f"DECISION: Open -> {message}")
        return jsonify({"status": "success", "action": "sent_standard_sms", "message": message})
    else:
        message = f"Hi {contact_name}, Office closed. We will call tomorrow."
        logging.info(f"DECISION: Closed -> {message}")
        return jsonify({"status": "success", "action": "sent_after_hours_sms", "message": message})

# --- 3. RUN THE SERVER ---
if __name__ == "__main__":
    # Run locally on port 5000
    print("Showtechedge Automation API is running on port 5000...")
    app.run(port=5000, debug=True)