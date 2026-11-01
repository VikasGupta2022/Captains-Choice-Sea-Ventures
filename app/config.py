import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow"
    )

    APP_NAME: str = "Captain's Choice Sea Ventures"
    APP_TAGLINE: str = "Fastest Mumbai-Mandwa Transfers & Luxury Harbor Cruises"
    APP_URL: str = "http://localhost:8000"
    
    # WhatsApp Integration
    WHATSAPP_PHONE: str = "917506920614"
    WHATSAPP_DISPLAY_PHONE: str = "+91 7506920614"
    WHATSAPP_DEFAULT_MESSAGE: str = "Hello Captain's Choice! I'd like to inquire about booking a speedboat charter."
    
    # Location & Contact
    CONTACT_EMAIL: str = "gatewayspeedboat@gmail.com"
    JETTY_LOCATION: str = "Jetty No. 5, Opposite The Taj Mahal Palace, Gateway of India, Colaba, Mumbai - 400001"
    GOOGLE_MAPS_URL: str = "https://maps.google.com/?q=Jetty+No+5+Gateway+of+India+Mumbai"
    
    # Razorpay Gateway
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_dummy_key123")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "dummy_secret_key456")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "dummy_webhook_secret789")
    
    # Database
    DATABASE_PATH: str = "/tmp/speedboat.db" if os.getenv("VERCEL") else str(BASE_DIR / "speedboat.db")
    
    # Auto-detect simulation mode: True if placeholder keys are used
    @property
    def is_razorpay_mock(self) -> bool:
        return (
            not self.RAZORPAY_KEY_ID 
            or "dummy" in self.RAZORPAY_KEY_ID.lower() 
            or "placeholder" in self.RAZORPAY_KEY_ID.lower()
        )



settings = Settings()
