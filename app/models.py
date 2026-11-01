import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.database import Base

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String(32), unique=True, index=True, nullable=False)
    
    # Customer Details
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    
    # Trip & Vessel
    route_id = Column(String(50), nullable=False)
    route_name = Column(String(150), nullable=False)
    boat_id = Column(String(50), nullable=False)
    boat_name = Column(String(100), nullable=False)
    trip_type = Column(String(30), default="one_way") # one_way, round_trip, harbour_cruise
    
    # Schedule
    travel_date = Column(String(20), nullable=False)
    time_slot = Column(String(30), nullable=False)
    passengers = Column(Integer, default=1)
    
    # Add-ons & Notes
    addons_selected = Column(Text, default="[]") # JSON list of addon ids
    special_requests = Column(Text, nullable=True)
    
    # Pricing (in INR)
    total_fare = Column(Float, nullable=False)
    advance_required = Column(Float, nullable=False)
    balance_due = Column(Float, nullable=False, default=0.0)
    
    # Statuses
    payment_status = Column(String(30), default="pending") # pending, paid, failed
    booking_status = Column(String(30), default="pending") # pending, confirmed, cancelled
    
    # Razorpay Transaction
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String(32), index=True, nullable=False)
    razorpay_order_id = Column(String(100), nullable=False)
    razorpay_payment_id = Column(String(100), nullable=False)
    razorpay_signature = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(30), default="captured")
    verified_via = Column(String(50), default="client_verification") # client_verification, webhook
    created_at = Column(DateTime, default=utcnow)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), nullable=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)
    signature = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
