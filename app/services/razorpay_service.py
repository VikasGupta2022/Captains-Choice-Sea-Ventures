import hmac
import hashlib
import time
import uuid
import requests
from typing import Dict, Any, Tuple
from app.config import settings

class RazorpayService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.is_mock = settings.is_razorpay_mock

    def create_order(self, amount_inr: float, receipt_id: str, notes: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a Razorpay order.
        Amount must be in paise (1 INR = 100 paise).
        """
        amount_paise = int(round(amount_inr * 100))

        if self.is_mock:
            # Generate simulated mock order
            mock_order_id = f"order_mock_{uuid.uuid4().hex[:14]}"
            return {
                "id": mock_order_id,
                "entity": "order",
                "amount": amount_paise,
                "amount_paid": 0,
                "amount_due": amount_paise,
                "currency": "INR",
                "receipt": receipt_id,
                "status": "created",
                "attempts": 0,
                "notes": notes or {},
                "is_mock": True
            }

        # Real Razorpay REST API call
        url = "https://api.razorpay.com/v1/orders"
        payload = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt_id,
            "notes": notes or {}
        }
        response = requests.post(
            url,
            json=payload,
            auth=(self.key_id, self.key_secret),
            timeout=10
        )
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Razorpay Order creation failed: {response.status_code} {response.text}")
        
        data = response.json()
        data["is_mock"] = False
        return data

    def verify_payment_signature(self, order_id: str, payment_id: str, razorpay_signature: str) -> bool:
        """
        Verify payment signature sent back from client Razorpay checkout handler:
        signature = HMAC_SHA256(order_id + "|" + payment_id, secret)
        """
        if self.is_mock:
            # Allow mock signatures if in test simulation
            if razorpay_signature.startswith("mock_sig_") or razorpay_signature == "simulated_success_signature":
                return True
        
        message = f"{order_id}|{payment_id}".encode("utf-8")
        secret = self.key_secret.encode("utf-8")
        expected_sig = hmac.new(secret, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, razorpay_signature)

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str) -> bool:
        """
        Verify incoming webhook from Razorpay:
        signature = HMAC_SHA256(raw_body, webhook_secret)
        """
        if not signature_header:
            return False
        
        secret = self.webhook_secret.encode("utf-8")
        expected_sig = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature_header)

    def generate_mock_payment_credentials(self, order_id: str) -> Tuple[str, str]:
        """Generate valid mock payment_id and signature for testing sandbox UI"""
        payment_id = f"pay_mock_{uuid.uuid4().hex[:14]}"
        message = f"{order_id}|{payment_id}".encode("utf-8")
        secret = self.key_secret.encode("utf-8")
        sig = hmac.new(secret, message, hashlib.sha256).hexdigest()
        return payment_id, sig

razorpay_service = RazorpayService()
