# Captain's Choice Sea Ventures — Design System & UI Architecture Guide

This comprehensive guide details the design tokens, visual hierarchy, responsive architecture, interactive animations, and component conventions for **Captain's Choice Sea Ventures** (`https://gatewayspeedboat.com/`).

---

## 1. Architecture Philosophy (90% Shared Responsive, 10% Adaptive)

To avoid component fragmentation and guarantee seamless cross-device performance, the platform adheres to a strict single responsive codebase:
- **Max Container:** `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` across all viewports.
- **Responsive Layout Grids:**
  - **Mobile (< 768px):** 1 column vertical stack with compact typography and fixed bottom action bar.
  - **Tablet / iPad (768px – 1024px):** 2 column grid for cards and forms.
  - **Desktop (≥ 1024px):** 12-column split (e.g. Hero: 7 cols value proposition, 5 cols interactive quick-quote card).
- **Navigation Adaptation:**
  - **Top Navbar:** Glassmorphism sticky header (`backdrop-blur-md bg-white/85 border-b border-slate-900/5`). Full links on `md:flex`; hamburger drawer on mobile.
  - **Sticky Bottom Action Bar (Mobile Only):** `md:hidden fixed bottom-0 left-0 right-0 z-40 backdrop-blur-md bg-white/90` with `[WhatsApp] | [Call] | [Book Boat ->]`. Completely hidden on tablet and desktop.
  - **Zero Floating Clutter:** The floating green circular WhatsApp widget has been permanently removed across all breakpoints, eliminating layout overlap.

---

## 2. Color Palette, Typography & Surface Tokens

| Token Name | Hex Code / Tailwind Class | Primary Usage |
| :--- | :--- | :--- |
| **Crisp Alabaster** | `#F8FAFC` (`bg-[#F8FAFC]`) | Global body canvas; subtle off-white contrast against pure white cards. |
| **Pure White** | `#FFFFFF` (`bg-white`) | Card surfaces, modals, popovers, and input fields. |
| **Deep Maritime Navy** | `#0B192C` (`bg-[#0B192C]`, `text-[#0B192C]`) | Primary typography, primary CTA buttons, top status strip, and footer. |
| **Ocean Cyan Accent** | `#0284C7` (`text-[#0284C7]`, `border-[#0284C7]`) | Key headline highlights ("18–20 Mins"), active pill indicators, and links. |
| **Sandstone Gold** | `#D97706` (`text-[#D97706]`) | Passenger star ratings (4.9 ★), sunset cruise badges, and ticket refs. |
| **Soft Mint Surface** | `bg-emerald-50 text-emerald-800 border-emerald-200` | Refined WhatsApp desk badges and action buttons (replaces neon green). |

### Typography Tokens
- **Heading Font:** `Outfit` (`font-display`) with `tracking-tight` (`letter-spacing: -0.025em`).
- **Body Font:** `Plus Jakarta Sans` (`font-sans`) for legibility in booking forms and specs.
- **Card Shadows:** Soft layered depth using `shadow-[0_8px_30px_rgb(0,0,0,0.06)] ring-1 ring-slate-900/5 rounded-2xl` (replaces hard grey borders).
- **Button Micro-Interactions:** `active:scale-[0.98] transition-all duration-200` on all interactive buttons.

---

## 3. Live Harbour Status Strip

Located at the very top of the viewport in Deep Maritime Navy (`bg-[#0B192C] text-white text-xs py-2 px-4`):
- **Live Harbour Pulse:** Pulsing green radar dot (`animate-ping` + solid green inner dot) indicating:
  > `"Jetty No. 5 (Apollo Bandar) Open • 🌊 Sea State: Calm • ⏱️ Mandwa Crossing: ~18 Mins"`
- **Desk Shortcut:** Direct link to WhatsApp desk `+91 7506920614` in soft mint styling.

---

## 4. Hero Section & Interactive Quick-Quote Fare Calculator

The Hero section employs a 12-column desktop split:
- **Left (7 Columns):**
  - Gateway No. 5 status badge.
  - H1 headline with Ocean Cyan highlight.
  - Trust metrics divided by hairlines:
    `18 Mins Transit` | `Jetty No. 5 (Opp. Taj Hotel)` | `4.9 ★ Verified Rating`.
  - Background line-art watermarks (5% opacity) of **Gateway of India arch** on the left and **Mandwa coastal palms** on the right.
- **Right (5 Columns) — Floating Fare Checker:**
  - **Route Pills:** `Gateway ⇄ Mandwa`, `Elephanta Tour`, `Harbour Cruise`.
  - **Vessel Size Pills:** `6–8 Pax Speedboat`, `12+ Pax Yacht`.
  - **Real-Time Reactive Price:** Instant DOM calculation without page refresh:
    - *Speedboat Mandwa:* `₹6,500 / whole boat` ("Approx. ₹1,080 per guest for 6 guests").
    - *Yacht Mandwa:* `₹25,000 / whole boat` ("Approx. ₹1,660 per guest for 15 guests").
  - **CTA Button:** `Check Available Slots →` auto-links to `/book?route=...&boat=...`.

---

## 5. Interactive Speedboat Transit Animation

Situated directly below the Hero section:
- **Left Heritage Node:** Minimalist SVG of **Gateway of India Arch** labeled `Mumbai (Jetty No. 5)`.
- **Right Coastal Node:** Minimalist SVG of **Mandwa Coastal Palms & Pier** labeled `Alibaug (Mandwa Jetty)`.
- **Connecting Track:** Wave ripple corridor connecting Mumbai and Alibaug.
- **Gliding Speedboat SVG (< 4KB):**
  - Smooth 14-second horizontal glide keyframe animation (`boatGlide`).
  - Subtle fading white/cyan wake trail (`wakePulse`).
  - Automatically reverses and scales direction when arriving at Mandwa.
- **Wave Divider:** Subtle slow-moving SVG wave divider (`6s` loop `waveFloat`) smoothly transitioning into the transfer cards.

---

## 6. Luxury Boarding Pass Route Cards

Styled to resemble premium marine boarding passes:
- **High-Resolution Maritime Imagery:**
  - High-speed twin-engine boat cutting azure wakes in Mumbai Harbour.
  - Smooth coastal approach to Mandwa Pier.
  - Golden hour sunset cruise across the harbour.
- **Floating Glassmorphic Badges:**
  - Top-Left: Duration (`⏱️ 18–20 Mins`) in `backdrop-blur-md bg-white/90`.
  - Top-Right: Vessel Type (`Private Boat • Up to 8 Guests`).
- **Scannable Spec Pills:** `[⚡ Twin-Engine]`, `[👥 Max 6–8 Pax]`, `[🧳 Luggage Included]`.
- **Boarding Pass Divider:** Subtle horizontal dashed border (`border-t border-dashed border-slate-200`).
- **Transparent Pricing:** Clear `/ whole boat` label with subtext `(Up to 6–8 guests)` paired with a Deep Navy `[Reserve →]` pill button.

---

## 7. VIP Boarding 3-Step Visual Timeline

Positioned above the FAQ section to set guest expectations and eliminate boarding anxiety:
1. **01 — Arrive at Gate No. 5 (Opp. Taj Mahal Palace):** Skip public ferry lines; ground supervisor escorts party directly.
2. **02 — Board in 2 Minutes:** Step straight onto your private twin-engine speedboat on your exact reserved schedule.
3. **03 — Touch Down at Mandwa in 20 Mins:** Glide across calm harbour waters and skip 3.5 hours of highway traffic.

---

## 8. Modifying Assets & Future Changes

### To change images:
Open `app/data/fleet_catalog.json` and update the `"image"` field under `"routes"` or `"boats"`. Always use high-resolution maritime photography featuring speedboats cutting clean white wakes or luxury yachts.

### To adjust fare calculation matrix in the Hero Calculator:
Open `app/templates/index.html` and edit `fareMatrix` inside the `<script>` tag:
```javascript
const fareMatrix = {
    "gateway-mandwa": {
        "speedboat": { price: 6500, boatId: "speedboat-yamaha-8", perGuest: "Approx. ₹1,080 per guest for 6 guests." },
        "yacht": { price: 25000, boatId: "motor-yacht-majesty-15", perGuest: "Approx. ₹1,660 per guest for 15 guests." }
    },
    ...
};
```

### To run automated test suite:
```powershell
python -m pytest tests/ -v -p no:asyncio
```
All 10 tests verify route catalog parsing, signature validation, booking calculations, and Jinja template rendering.
