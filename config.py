"""
config.py
---------
Reads all secret keys from environment variables (never hard-coded).
If a key is missing, the related service runs in DEMO mode so the app
still works during the hackathon demo — real keys activate real calls.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent

# --- Claude (AI chat + voice parsing) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# --- Azure Speech (voice input) ---
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")

# --- Azure Maps (nearby farmers / geocoding) ---
AZURE_MAPS_KEY = os.getenv("AZURE_MAPS_KEY", "")

# Each service checks its own key. True = real API, False = demo fallback.
HAS_CLAUDE = bool(ANTHROPIC_API_KEY)
HAS_AZURE_SPEECH = bool(AZURE_SPEECH_KEY)
HAS_AZURE_MAPS = bool(AZURE_MAPS_KEY)
