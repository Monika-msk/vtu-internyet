from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from pathlib import Path
import csv

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "subscribers.csv"

app = FastAPI(title="VTU Internyet Subscriptions")

# Allow CORS so the static docs page can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this later
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

class SubscribePayload(BaseModel):
    email: EmailStr


def ensure_csv_exists():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "created_at_iso"])  # minimal header expected by watcher


def load_existing_emails() -> set:
    ensure_csv_exists()
    emails = set()
    with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("email") or "").strip().lower()
            if email:
                emails.add(email)
    return emails


def append_email(email: str):
    ensure_csv_exists()
    with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([email, datetime.now(timezone.utc).isoformat()])


@app.get("/")
async def root():
    return {"ok": True, "service": "vtu-internyet-subscriptions"}


@app.post("/subscribe")
async def subscribe(payload: SubscribePayload):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    existing = load_existing_emails()
    if email in existing:
        return {"ok": True, "message": "Already subscribed"}

    append_email(email)
    return {"ok": True, "message": "Subscribed"}


@app.get("/subscribers.csv")
async def subscribers_csv():
    ensure_csv_exists()
    # Return as text/csv
    content = DATA_FILE.read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="text/csv")
