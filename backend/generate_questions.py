import json
import random
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "questions_generated.json"


def make_options(correct_answer: int, spread: int = 10):
    options = {str(correct_answer)}

    while len(options) < 4:
        delta = random.randint(1, spread)
        sign = random.choice([-1, 1])
        candidate = correct_answer + sign * delta

        if candidate >= 0:
            options.add(str(candidate))

    options = list(options)
    random.shuffle(options)
    return options


def generate_math_addition(start_id: int, count: int, difficulty: str):
    questions = []
    current_id = start_id

    if difficulty == "easy":
        low, high = 1, 20
    elif difficulty == "medium":
        low, high = 20, 200
    else:
        low, high = 100, 1000

    for _ in range(count):
        a = random.randint(low, high)
        b = random.randint(low, high)
        answer = a + b

        questions.append({
            "id": current_id,
            "text": f"{a} + {b} = ?",
            "options": make_options(answer, spread=max(5, answer // 8)),
            "answer": str(answer)
        })
        current_id += 1

    return questions, current_id


def generate_math_subtraction(start_id: int, count: int, difficulty: str):
    questions = []
    current_id = start_id

    if difficulty == "easy":
        low, high = 5, 30
    elif difficulty == "medium":
        low, high = 30, 300
    else:
        low, high = 200, 1200

    for _ in range(count):
        a = random.randint(low, high)
        b = random.randint(low, a)
        answer = a - b

        questions.append({
            "id": current_id,
            "text": f"{a} - {b} = ?",
            "options": make_options(answer, spread=max(5, max(10, a // 10))),
            "answer": str(answer)
        })
        current_id += 1

    return questions, current_id


def generate_math_multiplication(start_id: int, count: int, difficulty: str):
    questions = []
    current_id = start_id

    if difficulty == "easy":
        a_low, a_high = 1, 10
        b_low, b_high = 1, 10
    elif difficulty == "medium":
        a_low, a_high = 2, 20
        b_low, b_high = 2, 12
    else:
        a_low, a_high = 10, 50
        b_low, b_high = 2, 20

    for _ in range(count):
        a = random.randint(a_low, a_high)
        b = random.randint(b_low, b_high)
        answer = a * b

        questions.append({
            "id": current_id,
            "text": f"{a} × {b} = ?",
            "options": make_options(answer, spread=max(6, answer // 6)),
            "answer": str(answer)
        })
        current_id += 1

    return questions, current_id


def generate_math_division(start_id: int, count: int, difficulty: str):
    questions = []
    current_id = start_id

    if difficulty == "easy":
        q_low, q_high = 1, 10
        d_low, d_high = 1, 10
    elif difficulty == "medium":
        q_low, q_high = 2, 20
        d_low, d_high = 2, 12
    else:
        q_low, q_high = 5, 30
        d_low, d_high = 2, 20

    for _ in range(count):
        quotient = random.randint(q_low, q_high)
        divisor = random.randint(d_low, d_high)
        dividend = quotient * divisor
        answer = quotient

        questions.append({
            "id": current_id,
            "text": f"{dividend} ÷ {divisor} = ?",
            "options": make_options(answer, spread=max(4, answer // 3 if answer > 3 else 4)),
            "answer": str(answer)
        })
        current_id += 1

    return questions, current_id


def generate_english_questions(start_id: int):
    current_id = start_id

    english_easy = [
        {"text": "Dog nghĩa là gì?", "options": ["Mèo", "Chó", "Cá", "Chim"], "answer": "Chó"},
        {"text": "Apple nghĩa là gì?", "options": ["Táo", "Cam", "Nho", "Chuối"], "answer": "Táo"},
        {"text": "Cat nghĩa là gì?", "options": ["Con mèo", "Con chó", "Con cá", "Con chim"], "answer": "Con mèo"},
        {"text": "Book nghĩa là gì?", "options": ["Quyển sách", "Cái bàn", "Cái ghế", "Cái bút"], "answer": "Quyển sách"},
    ]

    english_medium = [
        {"text": "She ____ a student.", "options": ["am", "is", "are", "be"], "answer": "is"},
        {"text": "They ____ my friends.", "options": ["am", "is", "are", "be"], "answer": "are"},
        {"text": "I ____ to school every day.", "options": ["go", "goes", "going", "gone"], "answer": "go"},
        {"text": "This ____ my teacher.", "options": ["am", "is", "are", "be"], "answer": "is"},
    ]

    english_hard = [
        {
            "text": "Choose the correct sentence.",
            "options": [
                "He go to school.",
                "He goes to school.",
                "He going to school.",
                "He are going to school."
            ],
            "answer": "He goes to school."
        },
        {
            "text": "Choose the correct sentence.",
            "options": [
                "They is my friends.",
                "They are my friends.",
                "They am my friends.",
                "They be my friends."
            ],
            "answer": "They are my friends."
        }
    ]

    def with_ids(items):
        nonlocal current_id
        result = []
        for item in items:
            result.append({
                "id": current_id,
                "text": item["text"],
                "options": item["options"],
                "answer": item["answer"]
            })
            current_id += 1
        return result

    return {
        "easy": with_ids(english_easy),
        "medium": with_ids(english_medium),
        "hard": with_ids(english_hard)
    }, current_id


def generate_vietnamese_questions(start_id: int):
    current_id = start_id

    vietnamese_easy = [
        {"text": "Trái nghĩa của 'cao' là gì?", "options": ["thấp", "to", "dài", "xa"], "answer": "thấp"},
        {"text": "Từ nào viết đúng?", "options": ["sum họp", "xum họp", "xung họp", "sung họp"], "answer": "sum họp"},
        {"text": "Trái nghĩa của 'nhanh' là gì?", "options": ["chậm", "cao", "to", "rộng"], "answer": "chậm"},
        {"text": "Từ nào là con vật?", "options": ["con mèo", "cái bàn", "quyển vở", "cây bút"], "answer": "con mèo"},
    ]

    vietnamese_medium = [
        {"text": "Từ 'dũng cảm' có nghĩa là gì?", "options": ["nhút nhát", "gan dạ", "lười biếng", "buồn bã"], "answer": "gan dạ"},
        {"text": "Từ nào là danh từ?", "options": ["chạy", "đẹp", "bàn", "cao"], "answer": "bàn"},
        {"text": "Từ nào là động từ?", "options": ["xinh", "học", "bàn", "đẹp"], "answer": "học"},
        {"text": "Từ nào là tính từ?", "options": ["đẹp", "bàn", "chạy", "sách"], "answer": "đẹp"},
    ]

    vietnamese_hard = [
        {
            "text": "Chọn câu viết đúng chính tả.",
            "options": [
                "Em đang học bài.",
                "Em đang hok bài.",
                "Em dang học bài.",
                "Em đang học bai."
            ],
            "answer": "Em đang học bài."
        },
        {
            "text": "Câu nào viết đúng?",
            "options": [
                "Trời hôm nay rất đẹp.",
                "Trời hom nay rất đẹp.",
                "Trời hôm nay rất dep.",
                "Trời hôm nay rát đẹp."
            ],
            "answer": "Trời hôm nay rất đẹp."
        }
    ]

    def with_ids(items):
        nonlocal current_id
        result = []
        for item in items:
            result.append({
                "id": current_id,
                "text": item["text"],
                "options": item["options"],
                "answer": item["answer"]
            })
            current_id += 1
        return result

    return {
        "easy": with_ids(vietnamese_easy),
        "medium": with_ids(vietnamese_medium),
        "hard": with_ids(vietnamese_hard)
    }, current_id


def main():
    next_id = 1

    math_easy_add, next_id = generate_math_addition(next_id, 120, "easy")
    math_easy_sub, next_id = generate_math_subtraction(next_id, 120, "easy")
    math_easy_mul, next_id = generate_math_multiplication(next_id, 80, "easy")
    math_easy_div, next_id = generate_math_division(next_id, 80, "easy")

    math_medium_add, next_id = generate_math_addition(next_id, 120, "medium")
    math_medium_sub, next_id = generate_math_subtraction(next_id, 120, "medium")
    math_medium_mul, next_id = generate_math_multiplication(next_id, 80, "medium")
    math_medium_div, next_id = generate_math_division(next_id, 80, "medium")

    math_hard_add, next_id = generate_math_addition(next_id, 120, "hard")
    math_hard_sub, next_id = generate_math_subtraction(next_id, 120, "hard")
    math_hard_mul, next_id = generate_math_multiplication(next_id, 80, "hard")
    math_hard_div, next_id = generate_math_division(next_id, 80, "hard")

    english_data, next_id = generate_english_questions(next_id)
    vietnamese_data, next_id = generate_vietnamese_questions(next_id)

    db = {
        "math": {
            "easy": math_easy_add + math_easy_sub + math_easy_mul + math_easy_div,
            "medium": math_medium_add + math_medium_sub + math_medium_mul + math_medium_div,
            "hard": math_hard_add + math_hard_sub + math_hard_mul + math_hard_div
        },
        "english": english_data,
        "vietnamese": vietnamese_data
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    total = (
        len(db["math"]["easy"]) +
        len(db["math"]["medium"]) +
        len(db["math"]["hard"]) +
        len(db["english"]["easy"]) +
        len(db["english"]["medium"]) +
        len(db["english"]["hard"]) +
        len(db["vietnamese"]["easy"]) +
        len(db["vietnamese"]["medium"]) +
        len(db["vietnamese"]["hard"])
    )

    print(f"Generated {total} questions -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()