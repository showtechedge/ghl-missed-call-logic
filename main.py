import logging
import datetime
import os
import hmac
import hashlib
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Security: Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configuration
OPEN_HOUR = int(os.getenv("OPEN_HOUR", 9))
CLOSE_HOUR = int(os.getenv("CLOSE_HOUR", 17))
SECRET_KEY = os.getenv("GHL_SECRET_KEY", "my_secret_key") 

# Load VIPs (Case-insensitive for robustness)
vip_env = os.getenv("VIP_NUMBERS", "+2348000000000,+2349000000000,Olushola")
# Store VIPs as lowercase for easier matching
VIP_NUMBERS = set(vip.strip().lower() for vip in vip_env.split(','))

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. HELPER FUNCTIONS ---

def verify_ghl_signature(payload_body, header_signature):
    """
    Security Check: Verifies that the webhook actually came from GHL.
    """
    if not header_signature:
        return False
    expected_hash = hmac.new(
        SECRET_KEY.encode(), 
        payload_body, 
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_hash, header_signature)

def parse_timestamp(ts):
    """
    Robust time parser: Handles Seconds, Milliseconds, and ISO Strings.
    """
    try:
        if isinstance(ts, (int, float)):
            if ts > 10000000000: # Assume milliseconds
                ts = ts / 1000.0
            return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
        if isinstance(ts, str):
            return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception as e:
        logging.warning(f"Timestamp parsing failed: {e}. Defaulting to NOW.")
    
    return datetime.datetime.now(datetime.timezone.utc)

def check_business_hours(dt_utc):
    lagos_time = dt_utc + datetime.timedelta(hours=1)
    return OPEN_HOUR <= lagos_time.hour < CLOSE_HOUR

# --- 3. THE WEBHOOK ROUTE ---
@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per minute")
def webhook():
    # 1. Security Check (Signature)
    # UNCOMMENT IN PRODUCTION:
    # signature = request.headers.get('X-GHL-Signature')
    # if not verify_ghl_signature(request.data, signature):
    #     logging.warning("Security Alert: Invalid Signature detected!")
    #     return jsonify({"error": "Unauthorized"}), 401

    payload = request.json
    if not payload:
        return jsonify({"error": "No data received"}), 400

    # 2. Extract Data
    contact_data = payload.get('contact', {})
    contact_phone = contact_data.get('phone', payload.get('phone', 'Unknown Number'))
    contact_name = contact_data.get('firstName', payload.get('firstName', 'Valued Client'))
    raw_timestamp = payload.get('timestamp', None)

    # 3. Robust Time Parsing
    call_time = parse_timestamp(raw_timestamp)
    
    logging.info(f"Received Call: {contact_name} ({contact_phone}) at {call_time}")

    # 4. Logic: VIP Check (Case-insensitive)
    is_vip = (contact_phone.lower() in VIP_NUMBERS) or (contact_name.lower() in VIP_NUMBERS)

    if is_vip:
        message = f"Hello {contact_name}, VIP Alert! Alerting personal assistant."
        logging.info(f"DECISION: VIP -> {message}")
        
        # TODO: Replace with real GHL SMS API call when authenticated
        # requests.post("https://services.leadconnectorhq.com/conversations/messages", json={...})
        
        return jsonify({"status": "success", "action": "sent_vip_sms", "message": message})

    # 5. Logic: Business Hours Check
    if check_business_hours(call_time):
        message = f"Hi {contact_name}, calling you back within the hour!"
        logging.info(f"DECISION: Open -> {message}")
        return jsonify({"status": "success", "action": "sent_standard_sms", "message": message})
    else:
        message = f"Hi {contact_name}, Office closed. We will call tomorrow."
        logging.info(f"DECISION: Closed -> {message}")
        return jsonify({"status": "success", "action": "sent_after_hours_sms", "message": message})

# --- 4. RUN THE SERVER ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    print(f"Showtechedge Automation API starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)