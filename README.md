# 📞 GHL Missed Call Logic API (Enterprise Edition)
### Built by Showtechedge

A production-ready Microservice API designed to handle missed calls for GoHighLevel (GHL) sub-accounts. 

### 🌟 New Senior-Level Features
* **Security:** Rate Limiting (200 req/day) to prevent spam.
* **Robustness:** Smart Timestamp Parsing (ISO 8601 & Unix support).
* **Configurable:** Uses Environment Variables (no hardcoded settings).
* **Scalable:** Docker containerized for Cloud Run / Render.

---

## 🚀 Live API Endpoint
**Base URL:** `https://ghl-missed-call.onrender.com`

---

## ⚙️ Configuration (.env)
You can configure the behavior without touching the code by creating a `.env` file:

```text
# Timezone: Lagos (UTC+1) handling is built-in
OPEN_HOUR=9
CLOSE_HOUR=17

# Comma-separated list of VIPs (Names or Phone Numbers)
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

#### Scenario A: VIP Client
Triggered if the phone/name is in `VIP_NUMBERS`.

```json
{
  "status": "success",
  "action": "sent_vip_sms",
  "message": "Hello Olushola, VIP Alert! Alerting personal assistant."
}
```

#### Scenario B: Business Hours (Open)
Triggered between `OPEN_HOUR` and `CLOSE_HOUR` (Lagos Time).

```json
{
  "status": "success",
  "action": "sent_standard_sms",
  "message": "Hi Olushola, calling you back within the hour!"
}
```

#### Scenario C: After Hours (Closed)

```json
{
  "status": "success",
  "action": "sent_after_hours_sms",
  "message": "Hi Olushola, Office closed. We will call tomorrow."
}
```

---

## 🛠 Local Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/showtechedge/ghl-missed-call-logic.git
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Config**
   Create a `.env` file (see Configuration section above).

4. **Run Server**
   ```bash
   python main.py
   ```

---

**© 2026 Showtechedge.**
