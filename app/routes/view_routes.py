import json
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models import Booking, Payment, WebhookEvent
from app.config import settings, BASE_DIR
from app.services.booking_service import booking_service
from app.services.whatsapp_service import whatsapp_service

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

router = APIRouter(tags=["Views"])

def common_context(request: Request):
    return {
        "request": request,
        "app_name": settings.APP_NAME,
        "app_tagline": settings.APP_TAGLINE,
        "whatsapp_phone": settings.WHATSAPP_PHONE,
        "whatsapp_display_phone": settings.WHATSAPP_DISPLAY_PHONE,
        "whatsapp_default_url": whatsapp_service.get_general_inquiry_link(),
        "jetty_location": settings.JETTY_LOCATION,
        "google_maps_url": settings.GOOGLE_MAPS_URL,
        "contact_email": settings.CONTACT_EMAIL,
        "is_mock": settings.is_razorpay_mock
    }

@router.get("/")
def home_page(request: Request):
    ctx = common_context(request)
    ctx.update({
        "routes": booking_service.get_routes(),
        "boats": booking_service.get_fleet(),
        "addons": booking_service.get_addons(),
        "time_slots": booking_service.get_time_slots(),
        "active_nav": "home"
    })
    return templates.TemplateResponse(request=request, name="index.html", context=ctx)

@router.get("/fleet")
def fleet_page(request: Request, category: str = "all"):
    ctx = common_context(request)
    ctx.update({
        "boats": booking_service.get_fleet(category=category),
        "selected_category": category,
        "active_nav": "fleet"
    })
    return templates.TemplateResponse(request=request, name="fleet.html", context=ctx)

@router.get("/book")
def booking_page(request: Request, boat: str = "", route: str = "", trip_type: str = "one_way"):
    ctx = common_context(request)
    ctx.update({
        "routes": booking_service.get_routes(),
        "boats": booking_service.get_fleet(),
        "addons": booking_service.get_addons(),
        "time_slots": booking_service.get_time_slots(),
        "preselect_boat": boat,
        "preselect_route": route,
        "preselect_trip_type": trip_type,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "active_nav": "book"
    })
    return templates.TemplateResponse(request=request, name="booking.html", context=ctx)

@router.get("/booking/{booking_ref}")
def confirmation_page(booking_ref: str, request: Request, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.booking_ref == booking_ref).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking reference not found.")
    
    ctx = common_context(request)
    # Parse addons
    try:
        addon_ids = json.loads(booking.addons_selected or "[]")
    except Exception:
        addon_ids = []
    
    all_addons = {a["id"]: a for a in booking_service.get_addons()}
    selected_addons = [all_addons[aid] for aid in addon_ids if aid in all_addons]

    # Dynamic WhatsApp support link for this specific booking
    wa_support_url = whatsapp_service.get_booking_support_link(
        booking_ref=booking.booking_ref,
        customer_name=booking.customer_name,
        boat_name=booking.boat_name,
        travel_date=booking.travel_date
    )

    ctx.update({
        "booking": booking,
        "selected_addons": selected_addons,
        "wa_support_url": wa_support_url,
        "active_nav": "confirmation"
    })
    return templates.TemplateResponse(request=request, name="confirmation.html", context=ctx)

@router.get("/admin")
def admin_page(request: Request, db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(50).all()
    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(50).all()
    events = db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(50).all()
    
    ctx = common_context(request)
    ctx.update({
        "bookings": bookings,
        "payments": payments,
        "events": events,
        "total_revenue": sum(p.amount for p in payments if p.status == "captured"),
        "active_nav": "admin"
    })
    return templates.TemplateResponse(request=request, name="admin.html", context=ctx)
