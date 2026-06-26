"""
main.py
-------
Fallahy AI & Data Service — Rwan's part of the project.

This is a standalone API. The mobile app / Laravel backend just calls these
endpoints over HTTP. Run it with:

    uvicorn main:app --reload --port 8000

Interactive docs (try every endpoint in the browser):  http://localhost:8000/docs
"""
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import claude_chat
import voice
import maps
import analytics

app = FastAPI(
    title="Fallahy AI & Data Service",
    description="AI chat, Azure voice, Azure Maps, and price analytics for the Fallahy app.",
    version="1.0.0",
)

# Allow the mobile app / web frontend to call this during the hackathon.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- request models ----------
class ChatRequest(BaseModel):
    message: str
    role: str = "buyer"          # "buyer" or "farmer"
    history: list | None = None


class TextRequest(BaseModel):
    text: str


# ---------- health ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "Fallahy AI & Data Service"}


# ---------- 1) AI CHAT (Claude) ----------
@app.post("/api/ai/chat")
def ai_chat(req: ChatRequest):
    """Buyer/farmer question -> reply. May flag transfer_to_whatsapp=true."""
    return claude_chat.ask(req.message, req.role, req.history)


# ---------- 2) VOICE (Azure Speech + Claude parsing) ----------
@app.post("/api/voice/transcribe")
async def voice_transcribe(audio: UploadFile = File(...)):
    """Audio file -> Arabic text."""
    data = await audio.read()
    return voice.transcribe(data, audio.content_type or "audio/wav")


@app.post("/api/voice/parse-product")
def voice_parse_product(req: TextRequest):
    """Farmer speech text -> structured product (name, price, quantity)."""
    return voice.parse_product(req.text)


@app.post("/api/voice/parse-order")
def voice_parse_order(req: TextRequest):
    """Buyer speech text -> list of cart items."""
    return voice.parse_order(req.text)


# ---------- 3) MAPS (Azure Maps) ----------
@app.get("/api/maps/nearby-farmers")
def nearby_farmers(
    lat: float = Query(..., description="buyer latitude"),
    lng: float = Query(..., description="buyer longitude"),
    radius_km: float = 50,
    crop: str | None = None,
):
    """Farmers near the buyer, nearest first. Optional crop filter."""
    return maps.nearby_farmers(lat, lng, radius_km, crop)


# ---------- 4) ANALYTICS (data analysis) ----------
@app.get("/api/analytics/price-comparison")
def price_comparison(crop: str = Query(..., description="e.g. بندورة")):
    """Market vs Fallahy price + savings % (the WOW moment)."""
    return analytics.price_comparison(crop)


@app.get("/api/analytics/price-ticker")
def price_ticker():
    """Live stock-market style price ticker for all crops."""
    return analytics.price_ticker()


@app.get("/api/analytics/price-trend")
def price_trend(crop: str = Query(..., description="e.g. بندورة")):
    """Time series for a crop, for charts."""
    return analytics.price_trend(crop)


@app.get("/api/analytics/farmer-dashboard")
def farmer_dashboard(farmer_id: str = Query(..., description="e.g. F001")):
    """Revenue snapshot, best sellers, and smart alerts for a farmer."""
    return analytics.farmer_dashboard(farmer_id)
