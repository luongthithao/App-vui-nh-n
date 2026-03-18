from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
import random

app = FastAPI(title="Bee Learning API")

raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
     "http://127.0.0.1:5500,http://localhost:5500,https://fancy-tulumba-14bb7c.netlify.app"
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

if not QUESTIONS_FILE.exists():
    raise FileNotFoundError(f"Không tìm thấy file: {QUESTIONS_FILE}")

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    QUESTIONS_DB = json.load(f)


def get_question_pool(subject: str, difficulty: str):
    subject = subject.lower().strip()
    difficulty = difficulty.lower().strip()

    subject_data = QUESTIONS_DB.get(subject)
    if not subject_data:
        raise HTTPException(status_code=404, detail="Subject not found")

    pool = subject_data.get(difficulty)
    if pool:
        return pool

    if difficulty == "hard" and subject_data.get("medium"):
        return subject_data["medium"]

    if difficulty == "medium":
        if subject_data.get("easy"):
            return subject_data["easy"]
        if subject_data.get("hard"):
            return subject_data["hard"]

    if difficulty == "easy":
        if subject_data.get("medium"):
            return subject_data["medium"]
        if subject_data.get("hard"):
            return subject_data["hard"]

    raise HTTPException(status_code=404, detail="No questions available")


def parse_excluded_ids(exclude_ids: str):
    excluded_list = []

    if not exclude_ids.strip():
        return excluded_list

    for raw_id in exclude_ids.split(","):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            excluded_list.append(int(raw_id))

    return excluded_list


def choose_question(pool, excluded_list):
    if not pool:
        raise HTTPException(status_code=404, detail="No questions available")

    excluded_set = set(excluded_list)

    # 1) Ưu tiên câu hoàn toàn chưa dùng
    fresh_candidates = [q for q in pool if q["id"] not in excluded_set]
    if fresh_candidates:
        return random.choice(fresh_candidates)

    # 2) Nếu đã dùng nhiều, tránh lặp lại quá gần
    recent_20 = set(excluded_list[-20:]) if len(excluded_list) >= 20 else set(excluded_list)
    candidates_without_recent_20 = [q for q in pool if q["id"] not in recent_20]
    if candidates_without_recent_20:
        return random.choice(candidates_without_recent_20)

    # 3) Nới tiếp: chỉ tránh 10 câu gần nhất
    recent_10 = set(excluded_list[-10:]) if len(excluded_list) >= 10 else set(excluded_list)
    candidates_without_recent_10 = [q for q in pool if q["id"] not in recent_10]
    if candidates_without_recent_10:
        return random.choice(candidates_without_recent_10)

    # 4) Cuối cùng mới chọn lại toàn bộ pool
    return random.choice(pool)


@app.get("/")
def root():
    return {"message": "Bee Learning API running"}


@app.get("/health")
def health():
    total = 0
    per_subject = {}

    for subject_name, subject_data in QUESTIONS_DB.items():
        subject_total = 0
        for level_name, level_questions in subject_data.items():
            subject_total += len(level_questions)
        per_subject[subject_name] = subject_total
        total += subject_total

    return {
        "status": "ok",
        "questions_file": str(QUESTIONS_FILE),
        "total_questions": total,
        "questions_by_subject": per_subject
    }


@app.get("/question/{subject}/{difficulty}")
def get_question(subject: str, difficulty: str, exclude_ids: str = Query(default="")):
    pool = get_question_pool(subject, difficulty)
    excluded_list = parse_excluded_ids(exclude_ids)

    question = choose_question(pool, excluded_list)
    options = question["options"].copy()
    random.shuffle(options)

    return {
        "id": question["id"],
        "text": question["text"],
        "options": options,
        "answer": question["answer"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)