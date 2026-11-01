# Gateway Speed Boat & Marine Charters — Web Platform

A production-ready speedboat and ferry booking platform modeled after [Gateway Speed Boat](https://gatewayspeedboat.com), tailored for Mumbai to Mandwa (Alibaug), Elephanta Island, and harbour cruise charters.

Featuring the **Modern Coastal & Fast Transit** design language (Ocean Blue, Electric Cyan, Vibrant Coral), full responsiveness across **Mobile, iPad, and Desktop**, direct **WhatsApp (+91 7506920614)** click-to-chat integration, and **Razorpay Payment Gateway with Webhooks**.

---

## 🌟 Key Features

1. **Multi-Device Responsive Design**:
   - **📱 Mobile (<768px)**: Sticky bottom action bar ("Book Boat" + WhatsApp), off-canvas hamburger drawer, single-column tap-friendly booking wizard.
   - **📟 iPad / Tablet (768px - 1024px)**: 2-column split booking layout with live sticky boarding pass preview and price calculator.
   - **💻 Desktop (>1024px)**: Cinematic hero with quick booking widget, fleet showcase with speed & amenity badges, sticky navbar, and FAQ accordion.

2. **WhatsApp Integration (`+91 7506920614`)**:
   - Persistent floating WhatsApp button with pulse glow and quick tooltip.
   - Context-aware inquiry buttons on every boat card (auto-populates boat name, route, date, and passenger count into WhatsApp).
   - "Share on WhatsApp" and "Chat with Captain Desk" on confirmed E-Tickets.

3. **Razorpay Payment Gateway & Webhook**:
   - Dual-Mode: Built-in sandbox simulation mode for immediate zero-dependency testing, plus 100% compatible with real Razorpay Live/Test keys.
   - Secure HMAC-SHA256 signature verification for client checkouts.
   - Webhook listener at `/api/payments/webhook` validating `X-Razorpay-Signature` against `RAZORPAY_WEBHOOK_SECRET`.
   - Idempotent order state management (`pending` ➔ `paid`, `failed`).

4. **Future-Proof Modular Architecture**:
   - Fleet specifications, prices, routes, and departure slots are kept in `app/data/fleet_catalog.json` for instantaneous editing without code modifications.
   - SQLite database for persistent bookings, payment transactions, and webhook audit logs.
   - Admin overview dashboard at `/admin` with simulated webhook test dispatch tool.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Python 3.10+ (Python 3.13 is pre-installed).

### 2. Run the Application
From the project folder:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
👉 **http://127.0.0.1:8000**

---

## 🧭 Page Routes & Views

| URL | Description |
| :--- | :--- |
| **`http://127.0.0.1:8000/`** | **Homepage**: Hero banner, quick-search booking bar, fleet showcase, popular routes, reviews, FAQ. |
| **`http://127.0.0.1:8000/fleet`** | **Fleet Catalog**: Filterable tabs (Speedboats, Luxury Yachts, Sailboats) with technical specs & pricing. |
| **`http://127.0.0.1:8000/book`** | **Booking Wizard**: Step-by-step route, boat, date, time slot, guest details, and Razorpay checkout. |
| **`http://127.0.0.1:8000/booking/{ref}`** | **Boarding Pass & E-Ticket**: Printable ticket, QR pass, WhatsApp share, Jetty No. 5 directions. |
| **`http://127.0.0.1:8000/admin`** | **Admin Dashboard**: Live bookings list, payment ledger, and Razorpay webhook audit log. |
| **`http://127.0.0.1:8000/health`** | **Health Check**: Service status, WhatsApp configuration, and gateway mode. |

---

## ⚙️ Environment Configuration (`.env`)

```ini
APP_NAME="Gateway Speed Boat & Marine Charters"
APP_URL="http://localhost:8000"

# WhatsApp Business / Support Contact
WHATSAPP_PHONE="917506920614"
WHATSAPP_DISPLAY_PHONE="+91 7506920614"

# Razorpay Credentials (Leave as dummy for local simulation testing, or insert your real keys)
RAZORPAY_KEY_ID="rzp_test_dummy_key123"
RAZORPAY_KEY_SECRET="dummy_secret_key456"
RAZORPAY_WEBHOOK_SECRET="dummy_webhook_secret789"
```

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```powershell
python -m pytest tests/test_app.py -v -p no:asyncio
```

All 9 test cases cover:
- WhatsApp deep link generation & encoding
- Route fare calculation & round-trip discounts
- Razorpay client HMAC-SHA256 signature verification
- Razorpay Webhook HMAC-SHA256 signature verification
- End-to-end booking initiation, payment confirmation, and webhook state transitions.

---

## 📖 Further Documentation
See [`docs/CONFIGURATION_GUIDE.md`](docs/CONFIGURATION_GUIDE.md) for step-by-step instructions on adding new boats, changing fares, and setting up Razorpay Webhooks in production.
