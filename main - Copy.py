import datetime

# --- CONFIGURATION (Simulating GHL Settings) ---
BUSINESS_OPEN_HOUR = 9  # 9 AM
BUSINESS_CLOSE_HOUR = 17 # 5 PM
VIP_TAG = "VIP Client"

def handle_missed_call(contact_name, contact_tags, call_time_hour):
    """
    Decides the logic for a missed call based on Time and Tags.
    """
    print(f"--- Processing Missed Call from: {contact_name} ---")
    
    # 1. Check if it is outside business hours
    is_after_hours = call_time_hour < BUSINESS_OPEN_HOUR or call_time_hour >= BUSINESS_CLOSE_HOUR
    
    # 2. Check if contact is VIP
    is_vip = VIP_TAG in contact_tags

    # 3. LOGIC TREE
    if is_vip:
        # VIPs get a special message regardless of time
        return f"ACTION: Send SMS -> 'Hello {contact_name}, I saw you called. Since you are a VIP, I am alerting my personal assistant right now.'"
    
    elif is_after_hours:
        # Normal client, but office is closed
        return f"ACTION: Send SMS -> 'Hi {contact_name}, we are currently closed (Open 9am-5pm). We will call you back first thing tomorrow.'"
    
    else:
        # Normal client, during office hours (Maybe we were just busy)
        return f"ACTION: Send SMS -> 'Hey {contact_name}, sorry I missed you! I'm on another line. I'll call you back in 10 mins.'"

# --- SIMULATION (Testing the Code) ---
# Scenario A: A VIP calls at midnight
response_a = handle_missed_call(
    contact_name="Olushola", 
    contact_tags=["New Lead", "VIP Client"], 
    call_time_hour=23 # 11 PM
)
print(response_a)

print("\n")

# Scenario B: A New Lead calls at midnight
response_b = handle_missed_call(
    contact_name="John Doe", 
    contact_tags=["New Lead"], 
    call_time_hour=23 # 11 PM
)
print(response_b)