from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
import random

app = FastAPI()

raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500"
)

allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions_generated.json"

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    QUESTIONS_DB = json.load(f)


def get_question_pool(subject: str, difficulty: str):
    subject_data = QUESTIONS_DB.get(subject)
    if not subject_data:
        raise HTTPException(status_code=404, detail="Subject not found")

    pool = subject_data.get(difficulty)
    if pool:
        return pool

    if difficulty == "hard" and subject_data.get("medium"):
        return subject_data["medium"]

    if difficulty == "medium":
        if subject_data.get("hard"):
            return subject_data["hard"]
        if subject_data.get("easy"):
            return subject_data["easy"]

    if difficulty == "easy":
        if subject_data.get("medium"):
            return subject_data["medium"]

    raise HTTPException(status_code=404, detail="No questions available")


@app.get("/")
def root():
    return {"message": "Bee Learning API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/question/{subject}/{difficulty}")
def get_question(
    subject: str,
    difficulty: str,
    exclude_ids: str = Query(default="")
):
    pool = get_question_pool(subject, difficulty)

    excluded = set()
    if exclude_ids.strip():
        for raw_id in exclude_ids.split(","):
            raw_id = raw_id.strip()
            if raw_id.isdigit():
                excluded.add(int(raw_id))

    available = [q for q in pool if q["id"] not in excluded]

    if not available:
        raise HTTPException(
            status_code=409,
            detail=f"No unused questions available for {subject}/{difficulty}"
        )

    question = random.choice(available)
    options = question["options"].copy()
    random.shuffle(options)

    return {
        "id": question["id"],
        "text": question["text"],
        "options": options,
        "answer": question["answer"]
    }