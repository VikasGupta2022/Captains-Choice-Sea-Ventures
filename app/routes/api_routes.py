import json
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Booking, Payment, WebhookEvent
from app.config import settings
from app.services.booking_service import booking_service
from app.services.razorpay_service import razorpay_service
from app.services.whatsapp_service import whatsapp_service
from app.schemas import (
    CalculateFareRequest,
    FareBreakdownResponse,
    CreateBookingRequest,
    CreateBookingResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse
)

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/fleet")
def list_fleet(category: Optional[str] = None):
    return booking_service.get_fleet(category=category)

@router.get("/routes")
def list_routes():
    return booking_service.get_routes()

@router.get("/addons")
def list_addons():
    return booking_service.get_addons()

@router.get("/slots")
def list_slots(boat_id: Optional[str] = None, date: Optional[str] = None):
    return booking_service.get_time_slots()

@router.post("/bookings/calculate", response_model=FareBreakdownResponse)
def calculate_fare(req: CalculateFareRequest):
    try:
        fare_data = booking_service.calculate_fare(
            boat_id=req.boat_id,
            route_id=req.route_id,
            trip_type=req.trip_type,
            passengers=req.passengers,
            addon_ids=req.addons
        )
        return fare_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bookings/create", response_model=CreateBookingResponse)
def create_booking(req: CreateBookingRequest, db: Session = Depends(get_db)):
    try:
        fare = booking_service.calculate_fare(
            boat_id=req.boat_id,
            route_id=req.route_id,
            trip_type=req.trip_type,
            passengers=req.passengers,
            addon_ids=req.addons
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    booking_ref = booking_service.generate_booking_ref()

    # Create Razorpay Order for the advance amount (or full fare)
    try:
        razorpay_order = razorpay_service.create_order(
            amount_inr=fare["advance_required"],
            receipt_id=booking_ref,
            notes={
                "booking_ref": booking_ref,
                "boat_name": fare["boat_name"],
                "customer_name": req.customer_name,
                "customer_phone": req.customer_phone
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate payment gateway: {str(e)}")

    new_booking = Booking(
        booking_ref=booking_ref,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        route_id=req.route_id,
        route_name=fare["route_name"],
        boat_id=req.boat_id,
        boat_name=fare["boat_name"],
        trip_type=req.trip_type,
        travel_date=req.travel_date,
        time_slot=req.time_slot,
        passengers=req.passengers,
        addons_selected=json.dumps(req.addons),
        special_requests=req.special_requests,
        total_fare=fare["total_fare"],
        advance_required=fare["advance_required"],
        balance_due=fare["balance_due"],
        payment_status="pending",
        booking_status="pending",
        razorpay_order_id=razorpay_order["id"]
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return CreateBookingResponse(
        booking_ref=booking_ref,
        total_fare=fare["total_fare"],
        advance_required=fare["advance_required"],
        currency="INR",
        razorpay_order_id=razorpay_order["id"],
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        is_mock=razorpay_order.get("is_mock", False),
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        boat_name=fare["boat_name"],
        route_name=fare["route_name"],
        travel_date=req.travel_date,
        time_slot=req.time_slot
    )

@router.post("/payments/verify", response_model=VerifyPaymentResponse)
def verify_payment(req: VerifyPaymentRequest, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.booking_ref == req.booking_ref).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Verify signature
    is_valid = razorpay_service.verify_payment_signature(
        order_id=req.razorpay_order_id,
        payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature
    )
    if not is_valid:
        booking.payment_status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid Razorpay signature verification failed.")

    # Success: update booking
    booking.payment_status = "paid"
    booking.booking_status = "confirmed"
    booking.razorpay_payment_id = req.razorpay_payment_id
    
    # Record payment transaction
    payment_record = Payment(
        booking_ref=booking.booking_ref,
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
        amount=booking.advance_required,
        currency="INR",
        status="captured",
        verified_via="client_verification"
    )
    db.add(payment_record)
    db.commit()

    return VerifyPaymentResponse(
        success=True,
        message="Payment verified successfully. Speedboat booking confirmed!",
        booking_ref=booking.booking_ref,
        payment_status="paid",
        booking_status="confirmed"
    )

def process_webhook_payload(raw_body: bytes, signature: str, db: Session):
    """
    Synchronous core webhook processing logic:
    Verifies signature, logs event, and idempotently updates Booking and Payment records.
    """
    is_valid = razorpay_service.verify_webhook_signature(raw_body, signature)
    
    # In mock simulation mode, allow test signature header
    if not is_valid and settings.is_razorpay_mock:
        if signature.startswith("simulated_") or signature == "test_webhook_signature":
            is_valid = True

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        payload = {}

    event_id = payload.get("id") or payload.get("event_id")
    event_type = payload.get("event", "unknown")

    # Audit log the webhook event
    event_log = WebhookEvent(
        event_id=event_id,
        event_type=event_type,
        payload=raw_body.decode("utf-8", errors="ignore"),
        signature=signature,
        verified=is_valid
    )
    db.add(event_log)
    db.commit()

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid Razorpay Webhook Signature")

    # Process events idempotently
    event_data = payload.get("payload", {})
    payment_entity = event_data.get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    payment_id = payment_entity.get("id")
    
    if order_id:
        booking = db.query(Booking).filter(Booking.razorpay_order_id == order_id).first()
        if booking:
            if event_type in ("payment.captured", "order.paid"):
                booking.payment_status = "paid"
                booking.booking_status = "confirmed"
                if payment_id:
                    booking.razorpay_payment_id = payment_id

                # Save or update Payment record
                existing_payment = db.query(Payment).filter(
                    Payment.razorpay_order_id == order_id,
                    Payment.razorpay_payment_id == payment_id
                ).first()

                if not existing_payment:
                    pay_rec = Payment(
                        booking_ref=booking.booking_ref,
                        razorpay_order_id=order_id,
                        razorpay_payment_id=payment_id or "unknown",
                        razorpay_signature=signature,
                        amount=payment_entity.get("amount", booking.advance_required * 100) / 100,
                        currency="INR",
                        status="captured",
                        verified_via="webhook"
                    )
                    db.add(pay_rec)
                db.commit()

            elif event_type == "payment.failed":
                booking.payment_status = "failed"
                db.commit()

    return {"status": "ok", "event": event_type, "verified": True}

@router.post("/payments/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Razorpay Webhook endpoint.
    Verifies HMAC-SHA256 signature from X-Razorpay-Signature header.
    Processes: payment.captured, order.paid, payment.failed
    """
    raw_body = await request.body()
    return process_webhook_payload(raw_body, x_razorpay_signature or "", db)

@router.get("/whatsapp/link")
def get_whatsapp_link(boat: Optional[str] = None, route: Optional[str] = None, date: Optional[str] = None):
    if boat:
        return {"url": whatsapp_service.get_boat_inquiry_link(boat, route, date)}
    return {"url": whatsapp_service.get_general_inquiry_link()}
