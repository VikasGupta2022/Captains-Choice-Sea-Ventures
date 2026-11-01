import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings, BASE_DIR
from app.database import init_db
from app.routes.api_routes import router as api_router
from app.routes.view_routes import router as view_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables exist
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Speed Boat & Ferry Booking Platform for Gateway of India, Mandwa, Elephanta & Mumbai Harbour",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
static_dir = BASE_DIR / "app" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount Routers
app.include_router(view_router)
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "whatsapp_phone": settings.WHATSAPP_PHONE,
        "is_mock_payment": settings.is_razorpay_mock
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
