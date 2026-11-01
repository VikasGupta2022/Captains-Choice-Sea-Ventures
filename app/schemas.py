from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class CalculateFareRequest(BaseModel):
    boat_id: str
    route_id: str
    trip_type: str = "one_way" # one_way, round_trip, harbour_cruise
    passengers: int = Field(default=1, ge=1)
    addons: List[str] = []

class FareBreakdownResponse(BaseModel):
    boat_id: str
    boat_name: str
    route_id: str
    route_name: str
    trip_type: str
    passengers: int
    base_fare: float
    trip_multiplier: float
    addons_fare: float
    total_fare: float
    advance_required: float
    balance_due: float
    currency: str = "INR"

class CreateBookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_phone: str = Field(..., min_length=10)
    customer_email: Optional[str] = None
    boat_id: str
    route_id: str
    trip_type: str = "one_way"
    travel_date: str # YYYY-MM-DD
    time_slot: str
    passengers: int = Field(default=1, ge=1)
    addons: List[str] = []
    special_requests: Optional[str] = None

class CreateBookingResponse(BaseModel):
    booking_ref: str
    total_fare: float
    advance_required: float
    currency: str
    razorpay_order_id: str
    razorpay_key_id: str
    is_mock: bool
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    boat_name: str
    route_name: str
    travel_date: str
    time_slot: str

class VerifyPaymentRequest(BaseModel):
    booking_ref: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class VerifyPaymentResponse(BaseModel):
    success: bool
    message: str
    booking_ref: str
    payment_status: str
    booking_status: str
