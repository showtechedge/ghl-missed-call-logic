import logging
import datetime
import os

# --- 1. CONFIGURATION ---
# Define Business Hours (Lagos Time: UTC+1)
OPEN_HOUR = 9   # 9 AM
CLOSE_HOUR = 17 # 5 PM

# List of VIP Phone Numbers (Add your own or clients' numbers here)
VIP_NUMBERS = [
    "+2348000000000", 
    "+2349000000000",
    "Olushola" # Added for testing purposes
]

# Configure Logging (To see what's happening in the console)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_business_hours(timestamp_utc):
    """
    Check if a call came in during business hours (Lagos Time).
    Lagos is UTC+1.
    """
    # Convert UTC timestamp to a datetime object
    utc_time = datetime.datetime.fromtimestamp(timestamp_utc, datetime.timezone.utc)
    
    # Adjust to Lagos time (UTC + 1 hour)
    lagos_offset = datetime.timedelta(hours=1)
    lagos_time = utc_time + lagos_offset
    
    hour = lagos_time.hour
    
    # Check if within 9AM to 5PM
    is_open = OPEN_HOUR <= hour < CLOSE_HOUR
    return is_open, hour

def process_missed_call(payload):
    """
    Main logic to decide what SMS to send.
    """
    # 1. Extract Data (Handling both GHL "Flat" and "Nested" webhooks)
    contact_phone = payload.get('phone', payload.get('contact', {}).get('phone'))
    contact_name = payload.get('firstName', payload.get('contact', {}).get('firstName', 'Valued Client'))
    
    # FIX: Use timezone-aware object for current time instead of utcnow()
    current_utc_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
    timestamp = payload.get('timestamp', current_utc_timestamp)

    logging.info(f"Processing missed call for {contact_name} at {datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)} (UTC hour: {datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).hour})")

    # 2. Check VIP Status
    if contact_phone in VIP_NUMBERS or contact_name in VIP_NUMBERS:
        message = f"Hello {contact_name}, I saw you called. As a VIP client, I'm alerting my personal assistant right now. Expect a call back very soon!"
        logging.info(f"Decision: VIP → {message[:50]}...")
        return message

    # 3. Check Business Hours
    is_open, local_hour = check_business_hours(timestamp)
    
    if is_open:
        message = f"Hi {contact_name}, so sorry I missed your call! I'm currently in a meeting but will get back to you within the hour."
        logging.info(f"Decision: Business Hours (Lagos Hour: {local_hour}) → {message[:50]}...")
    else:
        message = f"Hi {contact_name}, thank you for reaching out! Our office is currently closed (open 9am–17pm Lagos time). We'll call you back first thing tomorrow. Have a great night!"
        logging.info(f"Decision: After Hours (Lagos Hour: {local_hour}) → {message[:50]}...")

    return message

# --- MOCK DATA FOR TESTING ---
if __name__ == "__main__":
    # Scenario A: VIP Client calling at night
    payload_vip = {
        "contact": {
            "firstName": "Olushola",
            "phone": "+2348123456789"
        },
        # Manually setting time to 9 PM UTC (10 PM Lagos)
        "timestamp": datetime.datetime(2026, 1, 9, 21, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
    }

    print("Scenario A (VIP at night - nested payload):")
    sms_a = process_missed_call(payload_vip)
    print(f"ACTION: Send SMS → '{sms_a}'\n")

    # Scenario B: Regular Client calling at night
    payload_regular = {
        "firstName": "John Doe",
        "phone": "+2349876543210",
        # Manually setting time to 9 PM UTC (10 PM Lagos)
        "timestamp": datetime.datetime(2026, 1, 9, 21, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
    }

    print("Scenario B (Normal at night - flat payload):")
    sms_b = process_missed_call(payload_regular)
    print(f"ACTION: Send SMS → '{sms_b}'\n")