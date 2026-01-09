# 📞 GHL Missed Call Logic API (Enterprise Edition)
### Built by Showtechedge

A production-ready Microservice API designed to handle missed calls for GoHighLevel (GHL) sub-accounts.

### 🌟 Senior-Level Features
* **Security:** Rate Limiting (200 req/day) & Signature Verification ready.
* **Robustness:** Smart Timestamp Parsing (ISO 8601 & Unix support).
* **Configurable:** Uses Environment Variables.
* **Scalable:** Docker containerized.

> **Security Note:** Signature verification is prepared but disabled for demo/testing. In production, uncomment the verification block in `main.py` and set `GHL_SECRET_KEY`.

---

## 🚀 Live API Endpoint
**Base URL:** `https://ghl-missed-call.onrender.com`

---

## ⚙️ Configuration (.env)
```text
# Timezone: Lagos (UTC+1) handling is built-in
OPEN_HOUR=9
CLOSE_HOUR=17

# Comma-separated list of VIPs
VIP_NUMBERS=+2348000000000,Olushola,ClientX

# Security settings
FLASK_DEBUG=False
GHL_SECRET_KEY=change_this_to_real_secret
```

---

## 📡 API Reference

### 1. Process Missed Call
**Endpoint:** `/webhook`
**Method:** `POST`
**Content-Type:** `application/json`

#### Request Body
The API accepts both "Flat" (Zapier) and "Nested" (GHL) payloads. It automatically detects timestamps in Seconds, Milliseconds, or ISO format.

**Example Request:**
```json
{
  "contact": {
    "firstName": "Olushola",
    "phone": "+2348000000000"
  },
  "timestamp": "2026-01-09T22:30:00Z"
}
```

### 🔄 Responses
* **VIP Client:** Returns `sent_vip_sms` action.
* **Business Hours (Open):** Returns `sent_standard_sms`.
* **After Hours (Closed):** Returns `sent_after_hours_sms`.

---

## 🧪 Testing Locally

You can test the API using `curl` in your terminal:

**1. Start the server:**
```bash
python main.py
```

**2. Send a test webhook:**
```bash
curl -X POST http://127.0.0.1:5000/webhook \
-H "Content-Type: application/json" \
-d '{"contact": {"firstName": "Olushola", "phone": "+2348000000000"}}'
```

---

**© 2026 Showtechedge.**
