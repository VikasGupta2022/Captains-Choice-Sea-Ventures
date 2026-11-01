# Gateway Speed Boat — Configuration & Maintenance Guide

This guide explains how to easily customize, update, and manage your speed boat ferry booking platform for any future changes without touching core code.

---

## 1. Changing WhatsApp Contact & Default Messages

All WhatsApp actions throughout the site are controlled by `.env` and `app/config.py`:

In `.env`:
```ini
# WhatsApp recipient number in international format (no spaces or plus sign)
WHATSAPP_PHONE="917506920614"

# Display text shown on navigation headers and footer
WHATSAPP_DISPLAY_PHONE="+91 7506920614"
```

### Context-Aware Messages
To customize what pre-filled messages are generated when a user clicks *"Ask Captain on WhatsApp"* or *"Inquire on WhatsApp"*, open:
`app/services/whatsapp_service.py`

Modify the helper methods:
- `get_general_inquiry_link()`: Default greeting from floating button.
- `get_boat_inquiry_link(boat_name, ...)`: When user clicks from a boat card.
- `get_booking_support_link(...)`: When user needs help with a confirmed ticket.

---

## 2. Managing Fleet, Prices & New Boats

All fleet information is stored in human-readable JSON at:
📂 `app/data/fleet_catalog.json`

### To Add a New Speedboat:
Add a new object inside the `"boats"` array:
```json
{
  "id": "speedboat-monterey-10",
  "name": "Monterey 270 Speed Cruiser",
  "category": "Speedboat",
  "capacity": 10,
  "speed_knots": 32,
  "pricing_type": "charter",
  "price_gateway_mandwa": 8500,
  "price_elephanta": 9500,
  "price_harbour_cruise": 5500,
  "advance_deposit": 2500,
  "badge": "⚡ New Addition",
  "featured": true,
  "engine": "Twin Mercury 200HP",
  "amenities": [
    "Twin Mercury Outboard",
    "Bimini Shade Canopy",
    "Marine Bluetooth Audio",
    "Safety Life Jackets"
  ],
  "image": "https://your-domain.com/static/images/monterey.jpg",
  "description": "High-performance coastal cruiser with plush seating."
}
```

### To Update Prices:
Simply change `price_gateway_mandwa`, `price_elephanta`, or `advance_deposit` in `app/data/fleet_catalog.json`. The booking price calculator updates immediately on the next page refresh without restarting the backend!

---

## 3. Adding or Updating Routes

In `app/data/fleet_catalog.json`, edit the `"routes"` array:
```json
{
  "id": "gateway-jnpt-mora",
  "name": "Gateway of India ➔ Mora Jetty (JNPT / Uran)",
  "origin": "Jetty 5, Gateway of India",
  "destination": "Mora Jetty, Uran",
  "duration": "15 Mins",
  "description": "Quick industrial transfer across the Mumbai harbour.",
  "distance_km": 10,
  "base_fare": 5000,
  "badge": "⚡ Express Route",
  "image": "https://..."
}
```

---

## 4. Configuring Razorpay Live Payment Gateway

### Step 1: Obtain Keys from Razorpay
1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com).
2. Go to **Settings** ➔ **API Keys**.
3. Generate **Key ID** and **Key Secret**.

### Step 2: Configure `.env`
Update `.env` in the root directory:
```ini
RAZORPAY_KEY_ID="rzp_live_xxxxxxxxxxxx"
RAZORPAY_KEY_SECRET="your_actual_key_secret"
RAZORPAY_WEBHOOK_SECRET="your_actual_webhook_secret"
```

Once real keys are configured, the site will automatically disable simulation mode and launch the official Razorpay Checkout popup modal on user checkout.

### Step 3: Webhook Setup in Razorpay Dashboard
1. Go to **Settings** ➔ **Webhooks** ➔ **Add New Webhook**.
2. Set Webhook URL: `https://your-domain.com/api/payments/webhook`.
3. Set Secret: The exact string you put in `RAZORPAY_WEBHOOK_SECRET`.
4. Select active events:
   - `payment.captured`
   - `order.paid`
   - `payment.failed`
5. Save Webhook.

---

## 5. Visual Theme Customization

The color system is defined in `app/templates/base.html` inside the `tailwind.config` block:
- **Ocean Blue:** `#0F2B48`
- **Electric Cyan:** `#0EA5E9` / `#06B6D4`
- **Sunset Coral:** `#F97316` / `#EA580C`

To tweak primary or accent brand colors, simply edit those 3 hex codes in `app/templates/base.html`.
