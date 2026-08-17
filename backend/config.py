import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# Database (PostgreSQL via Supabase)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Legacy SQLite (for local dev fallback)
DATABASE_PATH = BASE_DIR / "data" / "leads.db"

BRIEFS_DIR = Path(os.getenv("BRIEFS_DIR", "briefs"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

LEAD_STATUSES = [
    "scraped",
    "contacted",
    "responded",
    "confirmed",
    "brief_generated",
    "building",
    "done",
    "rejected",
]

LEAD_STATUS_LABELS = {
    "scraped": "Scrapeado",
    "contacted": "Contactado",
    "responded": "Respondido",
    "confirmed": "Confirmado",
    "brief_generated": "Brief Listo",
    "building": "Construyendo",
    "done": "Completado",
    "rejected": "Rechazado",
}
