import pytest
import hmac
import hashlib
import json
from unittest.mock import AsyncMock, MagicMock

from app.config import settings
from app.database import Base, engine, SessionLocal, init_db
from app.models import Booking, Payment, WebhookEvent
from app.services.booking_service import booking_service
from app.services.whatsapp_service import whatsapp_service
from app.services.razorpay_service import razorpay_service
from app.main import health_check
from app.routes.api_routes import (
    calculate_fare,
    create_booking,
    verify_payment,
    list_fleet,
    list_routes,
    list_addons,
    list_slots,
    process_webhook_payload
)
from app.schemas import (
    CalculateFareRequest,
    CreateBookingRequest,
    VerifyPaymentRequest
)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    yield

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_whatsapp_service_configuration():
    assert settings.WHATSAPP_PHONE == "917506920614"
    assert "7506920614" in whatsapp_service.get_base_url()
    
    # Test general inquiry link
    gen_link = whatsapp_service.get_general_inquiry_link()
    assert "https://wa.me/917506920614?text=" in gen_link

    # Test context boat inquiry link
    boat_link = whatsapp_service.get_boat_inquiry_link(
        boat_name="Speedster 24",
        route_name="Gateway to Mandwa",
        date="2026-11-05",
        passengers=6
    )
    assert "917506920614" in boat_link
    assert "Speedster" in boat_link

    # Test booking support link
    support_link = whatsapp_service.get_booking_support_link(
        booking_ref="GSB-20261101-ABCD",
        customer_name="John Doe",
        boat_name="Speedster 24",
        travel_date="2026-11-10"
    )
    assert "GSB-20261101-ABCD" in support_link
    assert "917506920614" in support_link

def test_booking_catalog_and_fare_calculation():
    routes = booking_service.get_routes()
    assert len(routes) >= 3
    
    boats = booking_service.get_fleet()
    assert len(boats) >= 4

    # Calculate fare for Gateway to Mandwa on Speedster 24
    fare = booking_service.calculate_fare(
        boat_id="speedboat-yamaha-8",
        route_id="gateway-mandwa",
        trip_type="one_way",
        passengers=4
    )
    assert fare["base_fare"] == 6500
    assert fare["total_fare"] == 6500
    assert fare["advance_required"] == 2000
    assert fare["balance_due"] == 4500

    # Calculate Round Trip with 10% discount multiplier (1.9x)
    rt_fare = booking_service.calculate_fare(
        boat_id="speedboat-yamaha-8",
        route_id="gateway-mandwa",
        trip_type="round_trip",
        passengers=4
    )
    assert rt_fare["total_fare"] == round(6500 * 1.90)

    # Calculate with add-on
    addons = booking_service.get_addons()
    assert len(addons) >= 1
    addon_id = addons[0]["id"]
    addon_price = addons[0]["price"]
    addon_fare = booking_service.calculate_fare(
        boat_id="speedboat-yamaha-8",
        route_id="gateway-mandwa",
        trip_type="one_way",
        passengers=4,
        addon_ids=[addon_id]
    )
    assert addon_fare["total_fare"] == 6500 + addon_price

def test_razorpay_hmac_signature_verification():
    order_id = "order_test_12345"
    payment_id = "pay_test_67890"
    secret = settings.RAZORPAY_KEY_SECRET

    # Valid signature
    message = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

    assert razorpay_service.verify_payment_signature(order_id, payment_id, valid_sig) is True
    # Tampered signature
    assert razorpay_service.verify_payment_signature(order_id, payment_id, "tampered_signature_123") is False

def test_razorpay_webhook_signature_verification():
    payload_body = b'{"event": "payment.captured", "id": "evt_123"}'
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

    valid_webhook_sig = hmac.new(webhook_secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    assert razorpay_service.verify_webhook_signature(payload_body, valid_webhook_sig) is True
    assert razorpay_service.verify_webhook_signature(payload_body, "invalid_webhook_sig") is False

def test_api_health():
    from app.main import health_check as main_health
    data = main_health()
    assert data["status"] == "healthy"
    assert data["app"] == "Captain's Choice Sea Ventures"
    assert data["whatsapp_phone"] == "917506920614"

def test_api_catalog_lists():
    fleet = list_fleet()
    assert len(fleet) >= 4
    
    speedboats = list_fleet(category="Speedboat")
    assert all(b["category"].lower() == "speedboat" for b in speedboats)

    routes = list_routes()
    assert len(routes) >= 3

    addons = list_addons()
    assert len(addons) >= 2

    slots = list_slots()
    assert "07:00 AM" in slots

def test_api_calculate_fare():
    req = CalculateFareRequest(
        boat_id="speedboat-yamaha-8",
        route_id="gateway-mandwa",
        trip_type="one_way",
        passengers=4,
        addons=[]
    )
    res = calculate_fare(req)
    assert res["total_fare"] == 6500
    assert res["advance_required"] == 2000
    assert res["balance_due"] == 4500

def test_full_booking_and_payment_flow(db_session):
    # 1. Create booking
    req = CreateBookingRequest(
        customer_name="Ananya Verma",
        customer_phone="917506920614",
        customer_email="ananya@example.com",
        boat_id="speedboat-yamaha-8",
        route_id="gateway-mandwa",
        trip_type="one_way",
        travel_date="2026-11-15",
        time_slot="10:00 AM",
        passengers=4,
        addons=[]
    )
    res = create_booking(req, db_session)
    assert res.booking_ref.startswith("GSB-")
    assert res.advance_required == 2000
    assert res.razorpay_order_id.startswith("order_")

    # Verify stored in DB with pending status
    booking = db_session.query(Booking).filter(Booking.booking_ref == res.booking_ref).first()
    assert booking is not None
    assert booking.payment_status == "pending"
    assert booking.booking_status == "pending"

    # 2. Verify payment (simulated signature)
    vreq = VerifyPaymentRequest(
        booking_ref=res.booking_ref,
        razorpay_order_id=res.razorpay_order_id,
        razorpay_payment_id="pay_sim_test_001",
        razorpay_signature="simulated_success_signature"
    )
    vres = verify_payment(vreq, db_session)
    assert vres.success is True
    assert vres.payment_status == "paid"
    assert vres.booking_status == "confirmed"

    # Re-query DB to check updated status
    db_session.refresh(booking)
    assert booking.payment_status == "paid"
    assert booking.booking_status == "confirmed"
    assert booking.razorpay_payment_id == "pay_sim_test_001"

    # Check payment record
    payment_rec = db_session.query(Payment).filter(Payment.booking_ref == res.booking_ref).first()
    assert payment_rec is not None
    assert payment_rec.amount == 2000.0

def test_razorpay_webhook_event_processing(db_session):
    import uuid
    # Prepare unique mock webhook request
    order_id = f"order_mock_test_webhook_{uuid.uuid4().hex[:6]}"
    booking_ref = f"GSB-TEST-{uuid.uuid4().hex[:6].upper()}"
    evt_id = f"evt_webhook_test_{uuid.uuid4().hex[:6]}"

    booking = Booking(
        booking_ref=booking_ref,
        customer_name="Webhook User",
        customer_phone="917506920614",
        route_id="gateway-mandwa",
        route_name="Gateway of India to Mandwa",
        boat_id="speedboat-yamaha-8",
        boat_name="Speedster 24 Twin Yamaha",
        trip_type="one_way",
        travel_date="2026-11-20",
        time_slot="11:00 AM",
        passengers=4,
        total_fare=6500,
        advance_required=2000,
        balance_due=4500,
        payment_status="pending",
        booking_status="pending",
        razorpay_order_id=order_id
    )
    db_session.add(booking)
    db_session.commit()

    webhook_payload = {
        "id": evt_id,
        "entity": "event",
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_webhook_captured_{uuid.uuid4().hex[:6]}",
                    "order_id": order_id,
                    "amount": 200000,
                    "currency": "INR",
                    "status": "captured"
                }
            }
        }
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    resp = process_webhook_payload(
        raw_body=raw_body,
        signature=sig,
        db=db_session
    )
    assert resp["status"] == "ok"
    assert resp["verified"] is True

    # Verify status changed in DB
    db_session.refresh(booking)
    assert booking.payment_status == "paid"
    assert booking.booking_status == "confirmed"

    # Verify webhook event was logged
    event_log = db_session.query(WebhookEvent).filter(WebhookEvent.event_id == evt_id).first()
    assert event_log is not None
    assert event_log.verified is True
