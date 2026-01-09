import logging
import datetime
import os
import hmac
import hashlib
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables from .env file (for local dev)
load_dotenv()

# --- 1. CONFIGURATION ---
app = Flask(__name__)

# Security: Rate Limiting (Prevent abuse)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configuration via Environment Variables (With defaults)
# This makes the code safe for production/enterprise use
OPEN_HOUR = int(os.getenv("OPEN_HOUR", 9))
CLOSE_HOUR = int(os.getenv("CLOSE_HOUR", 17))
SECRET_KEY = os.getenv("GHL_SECRET_KEY", "my_secret_key") 

# Load VIPs into a SET (Faster lookup than a list)
vip_env = os.getenv("VIP_NUMBERS", "+2348000000000,+2349000000000,Olushola")
VIP_NUMBERS = set(vip.strip() for vip in vip_env.split(','))

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. HELPER FUNCTIONS ---

def verify_ghl_signature(payload_body, header_signature):
    """
    Security Check: Verifies that the webhook actually came from GHL.
    (Note: This requires a real Shared Secret from GHL to work fully.)
    """
    if not header_signature:
        return False
    # Create the HMAC hash using your secret
    expected_hash = hmac.new(
        SECRET_KEY.encode(), 
        payload_body, 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, header_signature)

def parse_timestamp(ts):
    """
    Robust time parser. Handles:
    1. Unix Seconds (1736528...)
    2. Unix Milliseconds (1736528000...)
    3. ISO Strings ("2026-01-09T21:00:00")
    """
    try:
        # Case A: It's a number (float or int)
        if isinstance(ts, (int, float)):
            # If valid far in the future/past, it might be milliseconds
            if ts > 10000000000: 
                ts = ts / 1000.0
            return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
        
        # Case B: It's a String (ISO Format)
        if isinstance(ts, str):
            return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))

    except Exception as e:
        logging.warning(f"Timestamp parsing failed: {e}. Defaulting to NOW.")
    
    # Fallback: Return current UTC time
    return datetime.datetime.now(datetime.timezone.utc)

def check_business_hours(dt_utc):
    # Adjust to Lagos time (UTC + 1 hour)
    lagos_time = dt_utc + datetime.timedelta(hours=1)
    return OPEN_HOUR <= lagos_time.hour < CLOSE_HOUR

# --- 3. THE WEBHOOK ROUTE ---
@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per minute") # Extra strict limit for this specific endpoint
def webhook():
    # 1. Security Check (Signature)
    # In a real app, you would Uncomment the lines below to enforce security:
    # signature = request.headers.get('X-GHL-Signature')
    # if not verify_ghl_signature(request.data, signature):
    #     logging.warning("Security Alert: Invalid Signature detected!")
    #     return jsonify({"error": "Unauthorized"}), 401

    payload = request.json
    if not payload:
        return jsonify({"error": "No data received"}), 400

    # 2. Extract Data Safely (Using .get with defaults)
    contact_data = payload.get('contact', {})
    # Fallback to root level if not nested
    contact_phone = contact_data.get('phone', payload.get('phone', 'Unknown Number'))
    contact_name = contact_data.get('firstName', payload.get('firstName', 'Valued Client'))
    raw_timestamp = payload.get('timestamp', None)

    # 3. Robust Time Parsing
    call_time = parse_timestamp(raw_timestamp)
    
    logging.info(f"Received Call: {contact_name} ({contact_phone}) at {call_time}")

    # 4. Logic: VIP Check (O(1) lookup speed)
    # Check phone OR name (in a real app, prefer phone/email)
    if contact_phone in VIP_NUMBERS or contact_name in VIP_NUMBERS:
        message = f"Hello {contact_name}, VIP Alert! Alerting personal assistant."
        logging.info(f"DECISION: VIP -> {message}")
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
    # Check for 'PORT' env var (common in Cloud Run/Render)
    port = int(os.environ.get("PORT", 5000))
    # Disable debug mode in production for security
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"Showtechedge Automation API starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)