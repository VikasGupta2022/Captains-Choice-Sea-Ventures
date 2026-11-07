# Captain's Choice Sea Ventures — Luxury Speedboat Transfers & Charters

A luxury, minimalist maritime booking platform for **Captain's Choice Sea Ventures** operating private twin-engine speedboats between Gateway of India (Jetty No. 5), Mumbai and Mandwa Jetty, Alibaug (18–20 min crossing).

Featuring a **Maritime Minimalist design language** (Deep Maritime Navy `#0B192C`, Ocean Cyan `#0284C7`, Sandstone Gold `#D97706`, and Crisp Alabaster `#F8FAFC`), full responsiveness across **Mobile, Tablet, and Desktop**, direct **WhatsApp (+91 7506920614)** click-to-chat integration, and **Razorpay Payment Gateway with Webhooks**.

---

## 🌟 Key Features

1. **Multi-Device Responsive Design (90% Shared, 10% Adaptive)**:
   - **📱 Mobile (<768px)**: Sticky bottom action bar (`[WhatsApp]` | `[Call]` | `[Book Boat ->]`), off-canvas drawer navigation, uncluttered layout.
   - **📟 Tablet / iPad (768px - 1024px)**: 2-column split booking layout with live sticky boarding pass preview and price calculator.
   - **💻 Desktop (>1024px)**: 12-column split hero with live harbour status strip, interactive quick-quote fare calculator, animated speedboat transit corridor, and luxury boarding pass route cards.

2. **Live Harbour Status Strip**:
   - Pulsing maritime status indicator: `"Jetty No. 5 (Apollo Bandar) Open • 🌊 Sea State: Calm • ⏱️ Mandwa Crossing: ~18 Mins"`.

3. **Interactive Fare Checker & Speedboat Transit Animation**:
   - Instant quote calculator toggling route and vessel categories.
   - Lightweight SVG speedboat glide animation connecting Gateway of India Arch and Mandwa Coastal Palms.

4. **VIP Boarding 3-Step Visual Timeline**:
   - Clean 3-step walkthrough: Arrive at Gate No. 5, Board in 2 Minutes, Touch Down at Mandwa in 20 Mins.

5. **WhatsApp Integration (`+91 7506920614`)**:
   - Refined Soft Mint styling (`bg-emerald-50 text-emerald-800 border-emerald-200`).
   - Context-aware inquiry buttons on every boat card.
   - "Share on WhatsApp" and "Chat with Captain Desk" on confirmed E-Tickets.

6. **Razorpay Payment Gateway & Webhook**:
   - Dual-Mode: Built-in sandbox simulation mode for immediate zero-dependency testing, plus 100% compatible with real Razorpay Live/Test keys.
   - Secure HMAC-SHA256 signature verification for client checkouts.
   - Webhook listener at `/api/payments/webhook` validating `X-Razorpay-Signature` against `RAZORPAY_WEBHOOK_SECRET`.

---

## 📖 Complete Documentation
- 📘 [`docs/DESIGN_SYSTEM_AND_UI_GUIDE.md`](docs/DESIGN_SYSTEM_AND_UI_GUIDE.md): Color tokens, typography, SVG watermarks, keyframes, and layout architecture.
- 📙 [`docs/CONFIGURATION_GUIDE.md`](docs/CONFIGURATION_GUIDE.md): Managing fleet catalog, route pricing, and Razorpay production keys.

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
