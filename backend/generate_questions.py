import json
import random
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "questions_generated.json"


def unique_options(correct, candidates):
    options = [correct]
    for item in candidates:
        if item != correct and item not in options:
            options.append(item)
        if len(options) == 4:
            break

    while len(options) < 4:
        filler = f"{correct}*"
        if filler not in options:
            options.append(filler)

    random.shuffle(options)
    return options


def int_options(correct, spread_low=1, spread_high=10):
    wrongs = set()
    while len(wrongs) < 6:
        delta = random.randint(spread_low, spread_high)
        sign = random.choice([-1, 1])
        value = correct + delta * sign
        if value >= 0 and value != correct:
            wrongs.add(str(value))
    return unique_options(str(correct), list(wrongs))


def add_question(pool, qid, text, options, answer):
    pool.append({
        "id": qid,
        "text": text,
        "options": options,
        "answer": answer
    })


# =========================
# MATH
# =========================

def generate_math_easy(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["add", "sub", "mul", "div", "compare", "word"])

        if mode == "add":
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            ans = a + b
            add_question(pool, qid, f"{a} + {b} = ?", int_options(ans, 1, 8), str(ans))
            qid += 1

        elif mode == "sub":
            a = random.randint(10, 99)
            b = random.randint(1, a)
            ans = a - b
            add_question(pool, qid, f"{a} - {b} = ?", int_options(ans, 1, 8), str(ans))
            qid += 1

        elif mode == "mul":
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            ans = a * b
            add_question(pool, qid, f"{a} × {b} = ?", int_options(ans, 1, 10), str(ans))
            qid += 1

        elif mode == "div":
            b = random.randint(2, 10)
            ans = random.randint(2, 10)
            a = b * ans
            add_question(pool, qid, f"{a} ÷ {b} = ?", int_options(ans, 1, 6), str(ans))
            qid += 1

        elif mode == "compare":
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            correct = ">"
            if a < b:
                correct = "<"
            elif a == b:
                correct = "="
            add_question(pool, qid, f"{a} ... {b}", [">", "<", "=", "không biết"], correct)
            qid += 1

        elif mode == "word":
            a = random.randint(5, 30)
            b = random.randint(5, 30)
            ans = a + b
            text = f"Lan có {a} quả táo, mẹ cho thêm {b} quả. Lan có tất cả bao nhiêu quả?"
            add_question(pool, qid, text, int_options(ans, 1, 6), str(ans))
            qid += 1

    return pool, qid


def generate_math_medium(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["add", "sub", "mul", "div", "perimeter", "fraction", "word"])

        if mode == "add":
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            ans = a + b
            add_question(pool, qid, f"{a} + {b} = ?", int_options(ans, 5, 30), str(ans))
            qid += 1

        elif mode == "sub":
            a = random.randint(300, 1500)
            b = random.randint(50, a)
            ans = a - b
            add_question(pool, qid, f"{a} - {b} = ?", int_options(ans, 5, 30), str(ans))
            qid += 1

        elif mode == "mul":
            a = random.randint(11, 50)
            b = random.randint(2, 12)
            ans = a * b
            add_question(pool, qid, f"{a} × {b} = ?", int_options(ans, 5, 30), str(ans))
            qid += 1

        elif mode == "div":
            b = random.randint(2, 20)
            ans = random.randint(10, 50)
            a = b * ans
            add_question(pool, qid, f"{a} ÷ {b} = ?", int_options(ans, 2, 10), str(ans))
            qid += 1

        elif mode == "perimeter":
            l = random.randint(5, 30)
            w = random.randint(4, 20)
            ans = 2 * (l + w)
            text = f"Hình chữ nhật có chiều dài {l} cm, chiều rộng {w} cm. Chu vi là bao nhiêu?"
            add_question(pool, qid, text, int_options(ans, 2, 12), str(ans))
            qid += 1

        elif mode == "fraction":
            numerator = random.choice([2, 3, 4, 5, 6, 8])
            denominator = random.choice([2, 4, 8])
            if numerator % denominator == 0:
                ans = str(numerator // denominator)
            else:
                ans = f"{numerator}/{denominator}"
            text = f"Kết quả rút gọn của phân số {numerator}/{denominator} là?"
            options = [ans]
            if ans != "1":
                options += ["1", "2", f"{numerator}/{denominator}"]
            else:
                options += ["2", "1/2", "3/2"]
            options = options[:4]
            random.shuffle(options)
            add_question(pool, qid, text, options, ans)
            qid += 1

        elif mode == "word":
            a = random.randint(40, 150)
            b = random.randint(10, 50)
            c = random.randint(10, 50)
            ans = a - b + c
            text = f"Cửa hàng có {a} quyển vở, bán {b} quyển rồi nhập thêm {c} quyển. Còn lại bao nhiêu quyển?"
            add_question(pool, qid, text, int_options(ans, 3, 12), str(ans))
            qid += 1

    return pool, qid


def generate_math_hard(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["multi_step", "logic", "word", "perimeter", "average", "fraction"])

        if mode == "multi_step":
            a = random.randint(100, 500)
            b = random.randint(20, 100)
            c = random.randint(10, 80)
            ans = a + b - c
            text = f"Tính: {a} + {b} - {c} = ?"
            add_question(pool, qid, text, int_options(ans, 5, 25), str(ans))
            qid += 1

        elif mode == "logic":
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            c = random.randint(2, 5)
            ans = a * b + c
            text = f"Tính nhanh: {a} × {b} + {c} = ?"
            add_question(pool, qid, text, int_options(ans, 1, 10), str(ans))
            qid += 1

        elif mode == "word":
            box = random.randint(6, 20)
            each = random.randint(8, 25)
            extra = random.randint(10, 40)
            ans = box * each + extra
            text = f"Có {box} hộp bút, mỗi hộp có {each} chiếc. Thêm {extra} chiếc rời. Có tất cả bao nhiêu chiếc bút?"
            add_question(pool, qid, text, int_options(ans, 5, 30), str(ans))
            qid += 1

        elif mode == "perimeter":
            side = random.randint(5, 25)
            ans = side * 4
            text = f"Một hình vuông có cạnh dài {side} cm. Chu vi là bao nhiêu?"
            add_question(pool, qid, text, int_options(ans, 2, 14), str(ans))
            qid += 1

        elif mode == "average":
            a = random.randint(10, 40)
            b = random.randint(10, 40)
            c = random.randint(10, 40)
            ans = (a + b + c) // 3
            total = ans * 3
            a = random.randint(10, total - 20)
            b = random.randint(10, total - a - 10)
            c = total - a - b
            ans = total // 3
            text = f"Trung bình cộng của {a}, {b}, {c} là?"
            add_question(pool, qid, text, int_options(ans, 1, 8), str(ans))
            qid += 1

        elif mode == "fraction":
            text = "Phân số nào lớn hơn 1/2?"
            candidates = [("3/4", True), ("1/4", False), ("2/8", False), ("4/8", False)]
            random.shuffle(candidates)
            answer = next(x for x, ok in candidates if ok)
            options = [x for x, _ in candidates]
            add_question(pool, qid, text, options, answer)
            qid += 1

    return pool, qid


# =========================
# ENGLISH
# =========================

EN_VOCAB = {
    "dog": "con chó",
    "cat": "con mèo",
    "bird": "con chim",
    "fish": "con cá",
    "apple": "quả táo",
    "banana": "quả chuối",
    "school": "trường học",
    "teacher": "giáo viên",
    "book": "quyển sách",
    "pencil": "bút chì",
    "chair": "cái ghế",
    "table": "cái bàn",
    "house": "ngôi nhà",
    "car": "xe hơi",
    "sun": "mặt trời",
    "moon": "mặt trăng",
    "blue": "màu xanh dương",
    "red": "màu đỏ",
    "yellow": "màu vàng",
    "green": "màu xanh lá"
}

def generate_english_easy(start_id, count):
    pool = []
    qid = start_id
    words = list(EN_VOCAB.items())

    while len(pool) < count:
        mode = random.choice(["vocab", "simple_sentence", "color"])

        if mode == "vocab":
            en, vi = random.choice(words)
            wrongs = [x[1] for x in random.sample(words, 6) if x[1] != vi]
            options = unique_options(vi, wrongs)
            add_question(pool, qid, f'"{en}" nghĩa là gì?', options, vi)
            qid += 1

        elif mode == "simple_sentence":
            templates = [
                ("I ____ a student.", "am", ["is", "are", "be", "am"]),
                ("She ____ my friend.", "is", ["am", "are", "be", "is"]),
                ("They ____ playing.", "are", ["am", "is", "be", "are"]),
            ]
            text, ans, opts = random.choice(templates)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "color":
            color_map = {
                "red": "màu đỏ",
                "blue": "màu xanh dương",
                "yellow": "màu vàng",
                "green": "màu xanh lá"
            }
            en, vi = random.choice(list(color_map.items()))
            wrongs = [v for k, v in color_map.items() if v != vi]
            options = unique_options(vi, wrongs)
            add_question(pool, qid, f'"{en}" là màu gì?', options, vi)
            qid += 1

    return pool, qid


def generate_english_medium(start_id, count):
    pool = []
    qid = start_id

    sentence_templates = [
        ("My mother ____ a teacher.", "is", ["am", "are", "is", "be"]),
        ("We ____ in the classroom.", "are", ["am", "is", "are", "be"]),
        ("He ____ to school every day.", "goes", ["go", "goes", "going", "gone"]),
        ("I ____ my homework in the evening.", "do", ["does", "do", "did", "doing"]),
        ("The cat is ____ the table.", "under", ["under", "blue", "happy", "school"]),
    ]

    reorder_templates = [
        (["name", "What", "your", "is"], "What is your name?"),
        (["old", "How", "are", "you"], "How old are you?"),
        (["is", "This", "my", "book"], "This is my book."),
    ]

    while len(pool) < count:
        mode = random.choice(["grammar", "reorder", "choose"])

        if mode == "grammar":
            text, ans, opts = random.choice(sentence_templates)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "reorder":
            words, ans = random.choice(reorder_templates)
            wrongs = [
                " ".join(words) + "?",
                " ".join(reversed(words)) + "?",
                " ".join(words[:2] + words[2:]) + "."
            ]
            options = unique_options(ans, wrongs)
            add_question(pool, qid, f"Sắp xếp thành câu đúng: {' / '.join(words)}", options, ans)
            qid += 1

        elif mode == "choose":
            items = [
                (
                    "Choose the correct sentence.",
                    "She is my friend.",
                    ["She are my friend.", "She is my friend.", "She am my friend.", "She my friend is."]
                ),
                (
                    "Choose the correct sentence.",
                    "They are in the park.",
                    ["They is in the park.", "They are in the park.", "They am in the park.", "They in the park are."]
                ),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

    return pool, qid


def generate_english_hard(start_id, count):
    pool = []
    qid = start_id

    reading_templates = [
        (
            "Tom has 3 books. He buys 2 more books. How many books does Tom have?",
            "5",
            ["4", "5", "6", "7"]
        ),
        (
            "Lan goes to school at 7 o'clock. She goes home at 4 o'clock. Where does Lan go in the morning?",
            "school",
            ["home", "school", "park", "zoo"]
        ),
    ]

    grammar_templates = [
        (
            "Choose the correct sentence.",
            "He goes to school by bike.",
            [
                "He go to school by bike.",
                "He goes to school by bike.",
                "He going to school by bike.",
                "He are go to school by bike."
            ]
        ),
        (
            "Choose the correct sentence.",
            "My friends are playing football.",
            [
                "My friends is playing football.",
                "My friends are playing football.",
                "My friends am playing football.",
                "My friends playing football are."
            ]
        ),
    ]

    while len(pool) < count:
        mode = random.choice(["reading", "grammar"])

        if mode == "reading":
            text, ans, opts = random.choice(reading_templates)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "grammar":
            text, ans, opts = random.choice(grammar_templates)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

    return pool, qid


# =========================
# VIETNAMESE
# =========================

VIET_ANTONYMS = [
    ("cao", "thấp"),
    ("nhanh", "chậm"),
    ("to", "nhỏ"),
    ("xa", "gần"),
    ("vui", "buồn"),
    ("sáng", "tối"),
    ("mạnh", "yếu"),
    ("siêng năng", "lười biếng"),
]

VIET_POS = [
    ("bàn", "danh từ"),
    ("ghế", "danh từ"),
    ("học", "động từ"),
    ("chạy", "động từ"),
    ("đẹp", "tính từ"),
    ("cao", "tính từ"),
]

def generate_vietnamese_easy(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["antonym", "spelling", "meaning"])

        if mode == "antonym":
            word, ans = random.choice(VIET_ANTONYMS)
            wrongs = [x[1] for x in random.sample(VIET_ANTONYMS, 6) if x[1] != ans]
            options = unique_options(ans, wrongs)
            add_question(pool, qid, f'Trái nghĩa của "{word}" là gì?', options, ans)
            qid += 1

        elif mode == "spelling":
            items = [
                ("Từ nào viết đúng?", "sum họp", ["sum họp", "xum họp", "xung họp", "sung họp"]),
                ("Từ nào viết đúng?", "chăm chỉ", ["chăm chỉ", "trăm chỉ", "chăm chĩ", "trăm chĩ"]),
                ("Từ nào viết đúng?", "sạch sẽ", ["sạch sẽ", "sạch sẻ", "xạch sẽ", "sạch xẽ"]),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "meaning":
            items = [
                ("Từ “dũng cảm” có nghĩa là gì?", "gan dạ", ["gan dạ", "nhút nhát", "buồn bã", "lười biếng"]),
                ("Từ “siêng năng” có nghĩa là gì?", "chăm chỉ", ["chăm chỉ", "lười biếng", "ồn ào", "vui vẻ"]),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

    return pool, qid


def generate_vietnamese_medium(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["pos", "sentence", "meaning"])

        if mode == "pos":
            word, ans = random.choice(VIET_POS)
            opts = ["danh từ", "động từ", "tính từ", "đại từ"]
            random.shuffle(opts)
            add_question(pool, qid, f'Từ "{word}" thuộc loại từ nào?', opts, ans)
            qid += 1

        elif mode == "sentence":
            items = [
                ("Câu nào viết đúng chính tả?", "Em đang học bài.", ["Em đang học bài.", "Em đang hok bài.", "Em dang học bài.", "Em đang học bai."]),
                ("Câu nào viết đúng?", "Hôm nay trời rất đẹp.", ["Hôm nay trời rất đẹp.", "Hôm nay chời rất đẹp.", "Hôm nay trời rất đep.", "Hôm nay chời rất đep."]),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "meaning":
            items = [
                ("Từ nào gần nghĩa với “vui vẻ”?", "hạnh phúc", ["hạnh phúc", "buồn bã", "tức giận", "mệt mỏi"]),
                ("Từ nào gần nghĩa với “to lớn”?", "khổng lồ", ["khổng lồ", "nhỏ bé", "yếu ớt", "lẹ làng"]),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

    return pool, qid


def generate_vietnamese_hard(start_id, count):
    pool = []
    qid = start_id

    while len(pool) < count:
        mode = random.choice(["reading", "sentence_fix", "word_use"])

        if mode == "reading":
            text = "Đọc câu: “Lan rất chăm chỉ nên bạn luôn hoàn thành bài tập đúng giờ.” Từ nào cho biết tính cách của Lan?"
            ans = "chăm chỉ"
            opts = ["Lan", "đúng giờ", "chăm chỉ", "bài tập"]
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "sentence_fix":
            items = [
                (
                    "Chọn câu viết đúng ngữ pháp.",
                    "Chúng em đang chăm chú nghe giảng.",
                    [
                        "Chúng em đang chăm chú nghe giảng.",
                        "Chúng em chăm chú đang nghe giảng.",
                        "Chúng em đang nghe giảng chăm chú.",
                        "Chúng em nghe giảng đang chăm chú."
                    ]
                ),
                (
                    "Chọn câu viết đúng.",
                    "Buổi sáng, em tập thể dục cùng bố.",
                    [
                        "Buổi sáng, em tập thể dục cùng bố.",
                        "Buổi sáng em, tập thể dục cùng bố.",
                        "Buổi sáng, em cùng bố tập thể dục.",
                        "Buổi sáng, em tập cùng bố thể dục."
                    ]
                ),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

        elif mode == "word_use":
            items = [
                ('Từ nào dùng đúng trong câu: “Bạn Nam rất ____ nên ai cũng quý.”', "lễ phép", ["lễ phép", "ồn ào", "cẩu thả", "chậm chạp"]),
                ('Điền từ thích hợp: “Em luôn ____ bài trước khi đến lớp.”', "chuẩn bị", ["chuẩn bị", "vứt", "quên", "bỏ"]),
            ]
            text, ans, opts = random.choice(items)
            random.shuffle(opts)
            add_question(pool, qid, text, opts, ans)
            qid += 1

    return pool, qid


def main():
    qid = 1

    math_easy, qid = generate_math_easy(qid, 500)
    math_medium, qid = generate_math_medium(qid, 500)
    math_hard, qid = generate_math_hard(qid, 500)

    english_easy, qid = generate_english_easy(qid, 250)
    english_medium, qid = generate_english_medium(qid, 250)
    english_hard, qid = generate_english_hard(qid, 250)

    vietnamese_easy, qid = generate_vietnamese_easy(qid, 250)
    vietnamese_medium, qid = generate_vietnamese_medium(qid, 250)
    vietnamese_hard, qid = generate_vietnamese_hard(qid, 250)

    db = {
        "math": {
            "easy": math_easy,
            "medium": math_medium,
            "hard": math_hard
        },
        "english": {
            "easy": english_easy,
            "medium": english_medium,
            "hard": english_hard
        },
        "vietnamese": {
            "easy": vietnamese_easy,
            "medium": vietnamese_medium,
            "hard": vietnamese_hard
        }
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    total = (
        len(math_easy) + len(math_medium) + len(math_hard) +
        len(english_easy) + len(english_medium) + len(english_hard) +
        len(vietnamese_easy) + len(vietnamese_medium) + len(vietnamese_hard)
    )

    print(f"Generated {total} questions into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()