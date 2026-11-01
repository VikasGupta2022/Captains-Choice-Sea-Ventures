import urllib.parse
from app.config import settings

class WhatsAppService:
    def __init__(self):
        self.phone = settings.WHATSAPP_PHONE
        self.display_phone = settings.WHATSAPP_DISPLAY_PHONE

    def get_base_url(self) -> str:
        return f"https://wa.me/{self.phone}"

    def build_chat_link(self, message: str) -> str:
        """Create a direct WhatsApp link with pre-encoded message"""
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{self.phone}?text={encoded_message}"

    def get_general_inquiry_link(self) -> str:
        message = (
            f"Hello Captain's Choice! ⚓\n"
            f"I want to inquire about booking a speedboat or yacht charter from Gateway of India."
        )
        return self.build_chat_link(message)

    def get_boat_inquiry_link(self, boat_name: str, route_name: str = None, date: str = None, passengers: int = None) -> str:
        msg = f"Hello Captain's Choice! 🚤\nI am interested in booking the *{boat_name}*."
        if route_name:
            msg += f"\n• Route: {route_name}"
        if date:
            msg += f"\n• Date: {date}"
        if passengers:
            msg += f"\n• Guests: {passengers} passengers"
        msg += "\nPlease let me know the availability and best rate."
        return self.build_chat_link(msg)

    def get_booking_support_link(self, booking_ref: str, customer_name: str, boat_name: str, travel_date: str) -> str:
        msg = (
            f"Hello Captain's Choice Support! ⚓\n"
            f"My Booking Reference is *{booking_ref}* under name *{customer_name}*.\n"
            f"Boat: {boat_name}\n"
            f"Travel Date: {travel_date}\n"
            f"Could you please share the boarding jetty details and captain contact?"
        )
        return self.build_chat_link(msg)

whatsapp_service = WhatsAppService()
