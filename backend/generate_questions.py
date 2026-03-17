import argparse
import json
import math
import random
import unicodedata
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "questions_generated.json"
SEEN_KEYS = set()


# =========================================================
# CORE HELPERS
# =========================================================

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text).strip().lower())
    text = " ".join(text.split())
    return text


def can_continue(pool, count, attempts, max_attempts):
    return len(pool) < count and attempts < max_attempts


def unique_options(correct, candidates):
    correct = str(correct)
    options = [correct]

    for item in candidates:
        item = str(item)
        if item != correct and item not in options:
            options.append(item)
        if len(options) == 4:
            break

    filler_index = 1
    while len(options) < 4:
        filler = f"{correct}_{filler_index}"
        if filler not in options:
            options.append(filler)
        filler_index += 1

    random.shuffle(options)
    return options


def int_options(correct, spread_low=1, spread_high=10, minimum=0):
    correct = int(correct)
    candidates = set()

    for delta in range(spread_low, spread_high + 1):
        for sign in (-1, 1):
            value = correct + delta * sign
            if value >= minimum and value != correct:
                candidates.add(str(value))

    extra_delta = spread_high + 1
    safety = 0
    while len(candidates) < 10 and safety < 50:
        for sign in (-1, 1):
            value = correct + extra_delta * sign
            if value >= minimum and value != correct:
                candidates.add(str(value))
        extra_delta += 1
        safety += 1

    return unique_options(str(correct), list(candidates))


def float_options(correct, step=0.1):
    correct_val = round(float(correct), 2)
    candidates = set()

    for i in range(1, 9):
        for sign in (-1, 1):
            value = round(correct_val + sign * i * step, 2)
            if value != correct_val:
                candidates.add(str(value).rstrip("0").rstrip("."))

    extra = 9
    safety = 0
    while len(candidates) < 10 and safety < 30:
        for sign in (-1, 1):
            value = round(correct_val + sign * extra * step, 2)
            if value != correct_val:
                candidates.add(str(value).rstrip("0").rstrip("."))
        extra += 1
        safety += 1

    correct_str = str(correct_val).rstrip("0").rstrip(".")
    return unique_options(correct_str, list(candidates))


def build_question_key(text, options, answer):
    normalized_text = normalize_text(text)
    normalized_answer = normalize_text(answer)
    normalized_options = sorted(normalize_text(opt) for opt in options)
    return normalized_text + "||" + normalized_answer + "||" + "||".join(normalized_options)


def add_question(pool, qid, text, options, answer):
    key = build_question_key(text, options, answer)
    if key in SEEN_KEYS:
        return False, qid

    SEEN_KEYS.add(key)
    pool.append({
        "id": qid,
        "text": text,
        "options": options,
        "answer": str(answer)
    })
    return True, qid + 1


def sample_distinct(seq, k):
    if k >= len(seq):
        return random.sample(seq, len(seq))
    return random.sample(seq, k)


def eval_fraction(frac_str):
    a, b = frac_str.split("/")
    return int(a) / int(b)


# =========================================================
# MATH
# =========================================================

def generate_math_easy(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 50, 5000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "add_small",
            "sub_small",
            "mul_table",
            "div_exact",
            "compare_number",
            "missing_add",
            "missing_sub",
            "word_add_fruit",
            "word_sub_marbles",
            "next_number",
            "count_groups",
            "before_after"
        ])

        if mode == "add_small":
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            ans = a + b
            text = f"{a} + {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 8), ans)

        elif mode == "sub_small":
            a = random.randint(10, 99)
            b = random.randint(1, a)
            ans = a - b
            text = f"{a} - {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 8), ans)

        elif mode == "mul_table":
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            ans = a * b
            text = f"{a} × {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 10), ans)

        elif mode == "div_exact":
            b = random.randint(2, 10)
            ans = random.randint(2, 10)
            a = b * ans
            text = f"{a} ÷ {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 6), ans)

        elif mode == "compare_number":
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            correct = ">"
            if a < b:
                correct = "<"
            elif a == b:
                correct = "="
            text = f"{a} ... {b}"
            _, qid = add_question(pool, qid, text, [">", "<", "=", "không biết"], correct)

        elif mode == "missing_add":
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            total = a + b
            text = f"{a} + ? = {total}"
            _, qid = add_question(pool, qid, text, int_options(b, 1, 6), b)

        elif mode == "missing_sub":
            a = random.randint(10, 30)
            b = random.randint(1, min(15, a - 1))
            total = a + b
            text = f"{total} - ? = {a}"
            _, qid = add_question(pool, qid, text, int_options(b, 1, 6), b)

        elif mode == "word_add_fruit":
            a = random.randint(5, 30)
            b = random.randint(5, 30)
            ans = a + b
            subject = random.choice(["táo", "cam", "xoài", "quả lê"])
            name = random.choice(["Lan", "Mai", "Nam", "An"])
            text = f"{name} có {a} quả {subject}, được cho thêm {b} quả. {name} có tất cả bao nhiêu quả?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 6), ans)

        elif mode == "word_sub_marbles":
            a = random.randint(10, 30)
            b = random.randint(1, a - 1)
            ans = a - b
            name = random.choice(["Minh", "Bình", "Hà", "Thảo"])
            text = f"{name} có {a} viên bi, cho bạn {b} viên. {name} còn lại bao nhiêu viên bi?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 6), ans)

        elif mode == "next_number":
            start = random.randint(1, 50)
            step = random.choice([1, 2, 5])
            seq = [start + step * i for i in range(3)]
            ans = start + step * 3
            text = f"Số tiếp theo của dãy {seq[0]}, {seq[1]}, {seq[2]}, ... là?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 6), ans)

        elif mode == "count_groups":
            group = random.randint(2, 5)
            each = random.randint(2, 10)
            ans = group * each
            obj = random.choice(["bông hoa", "quyển vở", "cái bút"])
            text = f"Có {group} nhóm, mỗi nhóm có {each} {obj}. Có tất cả bao nhiêu {obj}?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 8), ans)

        elif mode == "before_after":
            n = random.randint(2, 99)
            ask = random.choice(["before", "after"])
            if ask == "before":
                text = f"Số liền trước của {n} là số nào?"
                ans = n - 1
            else:
                text = f"Số liền sau của {n} là số nào?"
                ans = n + 1
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 6), ans)

    print(f"[math/easy] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_math_medium(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 50, 5000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "add_large",
            "sub_large",
            "mul_medium",
            "div_medium",
            "perimeter_rectangle",
            "area_rectangle",
            "fraction_simplify",
            "fraction_compare",
            "word_inventory",
            "average_easy",
            "unit_convert",
            "time_elapsed"
        ])

        if mode == "add_large":
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            ans = a + b
            text = f"{a} + {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 5, 40), ans)

        elif mode == "sub_large":
            a = random.randint(400, 2000)
            b = random.randint(50, a - 10)
            ans = a - b
            text = f"{a} - {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 5, 40), ans)

        elif mode == "mul_medium":
            a = random.randint(11, 50)
            b = random.randint(2, 12)
            ans = a * b
            text = f"{a} × {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 5, 30), ans)

        elif mode == "div_medium":
            b = random.randint(2, 20)
            ans = random.randint(10, 60)
            a = b * ans
            text = f"{a} ÷ {b} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 2, 10), ans)

        elif mode == "perimeter_rectangle":
            l = random.randint(5, 30)
            w = random.randint(4, 20)
            ans = 2 * (l + w)
            text = f"Hình chữ nhật có chiều dài {l} cm, chiều rộng {w} cm. Chu vi là bao nhiêu?"
            _, qid = add_question(pool, qid, text, int_options(ans, 2, 16), ans)

        elif mode == "area_rectangle":
            l = random.randint(4, 20)
            w = random.randint(3, 15)
            ans = l * w
            text = f"Hình chữ nhật có chiều dài {l} cm, chiều rộng {w} cm. Diện tích là bao nhiêu cm²?"
            _, qid = add_question(pool, qid, text, int_options(ans, 2, 20), ans)

        elif mode == "fraction_simplify":
            d = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
            k = random.randint(2, 6)
            n = d * k
            n2 = random.randint(1, d - 1) * k
            n_use = n2 if random.random() < 0.75 else n
            g = math.gcd(n_use, n)
            a = n_use // g
            b = n // g
            ans = f"{a}/{b}" if b != 1 else str(a)
            wrongs = [
                f"{n_use}/{n}",
                f"{max(1, a + 1)}/{b}",
                f"{a}/{max(1, b + 1)}",
                "1"
            ]
            text = f"Rút gọn phân số {n_use}/{n} được:"
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "fraction_compare":
            a, b = random.choice([
                ("3/4", "1/2"),
                ("5/6", "2/3"),
                ("2/5", "3/5"),
                ("7/8", "5/8"),
            ])
            va = eval_fraction(a)
            vb = eval_fraction(b)
            ans = ">"
            if va < vb:
                ans = "<"
            elif va == vb:
                ans = "="
            text = f"{a} ... {b}"
            _, qid = add_question(pool, qid, text, [">", "<", "=", "không biết"], ans)

        elif mode == "word_inventory":
            a = random.randint(60, 180)
            b = random.randint(10, 60)
            c = random.randint(10, 60)
            ans = a - b + c
            item = random.choice(["quyển sách", "hộp bút", "quyển vở"])
            text = f"Cửa hàng có {a} {item}, bán {b} rồi nhập thêm {c}. Còn lại bao nhiêu {item}?"
            _, qid = add_question(pool, qid, text, int_options(ans, 3, 20), ans)

        elif mode == "average_easy":
            ans = random.randint(10, 50)
            a = ans + random.randint(-6, 6)
            b = ans + random.randint(-6, 6)
            c = ans * 3 - a - b
            if c <= 0:
                continue
            text = f"Trung bình cộng của {a}, {b}, {c} là?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 8), ans)

        elif mode == "unit_convert":
            unit = random.choice(["cm", "kg", "l"])
            if unit == "cm":
                value = random.randint(1, 20)
                ans = value * 100
                text = f"{value} m = ? cm"
            elif unit == "kg":
                value = random.randint(1, 12)
                ans = value * 1000
                text = f"{value} kg = ? g"
            else:
                value = random.randint(1, 12)
                ans = value * 1000
                text = f"{value} l = ? ml"
            _, qid = add_question(pool, qid, text, int_options(ans, 10, 300), ans)

        elif mode == "time_elapsed":
            start_hour = random.randint(1, 10)
            duration = random.randint(1, 6)
            ans = start_hour + duration
            text = f"Một bộ phim bắt đầu lúc {start_hour} giờ và kéo dài {duration} giờ. Phim kết thúc lúc mấy giờ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 4), ans)

    print(f"[math/medium] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_math_hard(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 50, 5000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "multi_step",
            "logic_order",
            "word_boxes",
            "square_perimeter",
            "average_three",
            "fraction_gt_half",
            "ratio_style",
            "unknown_equation",
            "decimal_add",
            "decimal_sub",
            "money_problem",
            "pattern_rule"
        ])

        if mode == "multi_step":
            a = random.randint(100, 800)
            b = random.randint(20, 150)
            c = random.randint(10, 90)
            ans = a + b - c
            text = f"Tính: {a} + {b} - {c} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 8, 30), ans)

        elif mode == "logic_order":
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            c = random.randint(2, 20)
            ans = a * b + c
            text = f"Tính nhanh: {a} × {b} + {c} = ?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 12), ans)

        elif mode == "word_boxes":
            box = random.randint(6, 20)
            each = random.randint(8, 25)
            extra = random.randint(10, 40)
            ans = box * each + extra
            text = f"Có {box} hộp bút, mỗi hộp có {each} chiếc. Thêm {extra} chiếc rời. Có tất cả bao nhiêu chiếc bút?"
            _, qid = add_question(pool, qid, text, int_options(ans, 10, 45), ans)

        elif mode == "square_perimeter":
            side = random.randint(5, 25)
            ans = side * 4
            text = f"Một hình vuông có cạnh dài {side} cm. Chu vi là bao nhiêu?"
            _, qid = add_question(pool, qid, text, int_options(ans, 2, 18), ans)

        elif mode == "average_three":
            ans = random.randint(12, 60)
            a = ans + random.randint(-10, 10)
            b = ans + random.randint(-10, 10)
            c = ans * 3 - a - b
            if c <= 0:
                continue
            text = f"Trung bình cộng của {a}, {b}, {c} là?"
            _, qid = add_question(pool, qid, text, int_options(ans, 2, 10), ans)

        elif mode == "fraction_gt_half":
            candidates = [("3/4", True), ("1/4", False), ("2/8", False), ("4/8", False)]
            random.shuffle(candidates)
            answer = next(x for x, ok in candidates if ok)
            options = [x for x, _ in candidates]
            text = "Phân số nào lớn hơn 1/2?"
            _, qid = add_question(pool, qid, text, options, answer)

        elif mode == "ratio_style":
            red = random.randint(2, 8)
            blue = random.randint(2, 8)
            ans = red + blue
            text = f"Một hộp có {red} bút đỏ và {blue} bút xanh. Hộp có tất cả bao nhiêu chiếc bút?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 8), ans)

        elif mode == "unknown_equation":
            x = random.randint(5, 60)
            b = random.randint(3, 20)
            total = x + b
            text = f"Tìm số thích hợp: ? + {b} = {total}"
            _, qid = add_question(pool, qid, text, int_options(x, 2, 10), x)

        elif mode == "decimal_add":
            a = round(random.randint(10, 90) / 10, 1)
            b = round(random.randint(10, 90) / 10, 1)
            ans = round(a + b, 1)
            text = f"{a} + {b} = ?"
            _, qid = add_question(pool, qid, text, float_options(ans, 0.1), ans)

        elif mode == "decimal_sub":
            a = round(random.randint(50, 150) / 10, 1)
            b = round(random.randint(10, int(a * 10) - 1) / 10, 1)
            ans = round(a - b, 1)
            text = f"{a} - {b} = ?"
            _, qid = add_question(pool, qid, text, float_options(ans, 0.1), ans)

        elif mode == "money_problem":
            a = random.randint(10, 50) * 1000
            b = random.randint(5, 20) * 1000
            ans = a + b
            text = f"Mẹ mua sách hết {a} đồng và mua thêm bút hết {b} đồng. Tổng cộng mẹ đã trả bao nhiêu tiền?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1000, 8000), ans)

        elif mode == "pattern_rule":
            start = random.randint(2, 20)
            step = random.choice([3, 4, 5, 6])
            seq = [start + step * i for i in range(4)]
            ans = start + step * 4
            text = f"Số tiếp theo của dãy {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ... là?"
            _, qid = add_question(pool, qid, text, int_options(ans, 1, 10), ans)

    print(f"[math/hard] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


# =========================================================
# ENGLISH DATA
# =========================================================

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
    "green": "màu xanh lá",
    "friend": "bạn bè",
    "family": "gia đình",
    "happy": "vui vẻ",
    "water": "nước",
    "milk": "sữa",
    "bread": "bánh mì",
    "pen": "cây bút",
    "bag": "cái cặp",
    "window": "cửa sổ",
    "door": "cánh cửa",
    "garden": "khu vườn",
    "flower": "bông hoa",
    "tree": "cái cây",
}

COLOR_MAP = {
    "red": "màu đỏ",
    "blue": "màu xanh dương",
    "yellow": "màu vàng",
    "green": "màu xanh lá",
    "black": "màu đen",
    "white": "màu trắng"
}


# =========================================================
# ENGLISH
# =========================================================

def generate_english_easy(start_id, count):
    pool = []
    qid = start_id
    words = list(EN_VOCAB.items())
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "vocab",
            "color",
            "be_verb",
            "choose_word",
            "plural",
            "matching_meaning",
            "simple_reading",
            "animal_sound",
            "classroom_object"
        ])

        if mode == "vocab":
            en, vi = random.choice(words)
            wrongs = [x[1] for x in sample_distinct(words, 8) if x[1] != vi]
            text = f'"{en}" nghĩa là gì?'
            _, qid = add_question(pool, qid, text, unique_options(vi, wrongs), vi)

        elif mode == "color":
            en, vi = random.choice(list(COLOR_MAP.items()))
            wrongs = [v for _, v in COLOR_MAP.items() if v != vi]
            text = f'"{en}" là màu gì?'
            _, qid = add_question(pool, qid, text, unique_options(vi, wrongs), vi)

        elif mode == "be_verb":
            subject, ans, wrongs = random.choice([
                ("I", "am", ["is", "are", "be"]),
                ("She", "is", ["am", "are", "be"]),
                ("They", "are", ["am", "is", "be"]),
                ("He", "is", ["am", "are", "be"]),
                ("We", "are", ["am", "is", "be"]),
            ])
            noun = random.choice(["a student", "happy", "my friend", "in the room"])
            text = f"{subject} ____ {noun}."
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "choose_word":
            text, ans, opts = random.choice([
                ("Choose the correct word: I have a ____.", "book", ["book", "blue", "run", "happy"]),
                ("Choose the correct word: She is my ____.", "friend", ["friend", "yellow", "jump", "apple"]),
                ("Choose the correct word: We study at ____.", "school", ["school", "banana", "red", "sing"]),
                ("Choose the correct word: The bird can ____.", "fly", ["fly", "table", "milk", "teacher"]),
                ("Choose the correct word: I put my books in my ____.", "bag", ["bag", "sun", "teacher", "sleep"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "plural":
            word = random.choice(["book", "cat", "dog", "apple", "flower", "pen"])
            ans = word + "s"
            wrongs = [word, word + "es", word + "ies"]
            text = f"Plural of '{word}' is?"
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "matching_meaning":
            text, ans, opts = random.choice([
                ('"happy" gần nghĩa nhất với từ nào?', "vui vẻ", ["buồn bã", "vui vẻ", "mệt", "tối"]),
                ('"water" nghĩa là gì?', "nước", ["lửa", "nước", "bàn", "sữa"]),
                ('"teacher" nghĩa là gì?', "giáo viên", ["học sinh", "giáo viên", "bác sĩ", "nông dân"]),
                ('"bread" nghĩa là gì?', "bánh mì", ["bánh mì", "quả táo", "bút chì", "trường học"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "simple_reading":
            text, ans, opts = random.choice([
                ("Tom has 2 apples. He gets 1 more apple. How many apples does Tom have?", "3", ["2", "3", "4", "5"]),
                ("Lan is in the classroom. Where is Lan?", "classroom", ["classroom", "park", "zoo", "home"]),
                ("My book is on the table. Where is my book?", "table", ["chair", "table", "school", "bag"]),
                ("Nam has a cat. The cat is black. What color is the cat?", "black", ["white", "yellow", "black", "green"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "animal_sound":
            animal, sound = random.choice([
                ("dog", "bark"),
                ("cat", "meow"),
                ("bird", "sing"),
            ])
            text = f"A {animal} can ____."
            wrongs = ["read", "draw", "jump"]
            _, qid = add_question(pool, qid, text, unique_options(sound, wrongs), sound)

        elif mode == "classroom_object":
            obj = random.choice(["book", "pen", "chair", "table", "bag", "pencil"])
            text = f"Which word names a classroom object?"
            wrongs = sample_distinct(["run", "blue", "happy", "sing", "jump", "green"], 3)
            _, qid = add_question(pool, qid, f"{text} ({obj})", unique_options(obj, wrongs), obj)

    print(f"[english/easy] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_english_medium(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "grammar",
            "reorder",
            "choose_sentence",
            "preposition",
            "daily_routine",
            "reading",
            "question_answer"
        ])

        if mode == "grammar":
            text, ans, opts = random.choice([
                ("My mother ____ a teacher.", "is", ["am", "are", "is", "be"]),
                ("We ____ in the classroom.", "are", ["am", "is", "are", "be"]),
                ("He ____ to school every day.", "goes", ["go", "goes", "going", "gone"]),
                ("I ____ my homework in the evening.", "do", ["does", "do", "did", "doing"]),
                ("She ____ milk every morning.", "drinks", ["drink", "drinks", "drinking", "drank"]),
                ("My brother ____ football after school.", "plays", ["play", "plays", "playing", "played"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "reorder":
            words, ans = random.choice([
                (["name", "What", "your", "is"], "What is your name?"),
                (["old", "How", "are", "you"], "How old are you?"),
                (["is", "This", "my", "book"], "This is my book."),
                (["goes", "He", "school", "to", "every", "day"], "He goes to school every day."),
                (["like", "I", "milk"], "I like milk."),
            ])
            wrongs = [
                " ".join(words) + "?",
                " ".join(reversed(words)) + "?",
                " ".join(words) + "."
            ]
            text = f"Sắp xếp thành câu đúng: {' / '.join(words)}"
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "choose_sentence":
            text, ans, opts = random.choice([
                ("Choose the correct sentence.", "She is my friend.", ["She are my friend.", "She is my friend.", "She am my friend.", "She my friend is."]),
                ("Choose the correct sentence.", "They are in the park.", ["They is in the park.", "They are in the park.", "They am in the park.", "They in the park are."]),
                ("Choose the correct sentence.", "My father goes to work by car.", ["My father go to work by car.", "My father goes to work by car.", "My father going to work by car.", "My father are go to work by car."]),
                ("Choose the correct sentence.", "I have two pencils.", ["I has two pencils.", "I have two pencils.", "I am two pencils.", "I having two pencils."]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "preposition":
            text, ans, opts = random.choice([
                ("The cat is ____ the table.", "under", ["under", "blue", "happy", "school"]),
                ("The ball is ____ the box.", "in", ["in", "run", "yellow", "teacher"]),
                ("The picture is ____ the wall.", "on", ["on", "drink", "book", "green"]),
                ("The school bag is ____ the chair.", "on", ["on", "under", "milk", "read"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "daily_routine":
            text, ans, opts = random.choice([
                ("I usually ____ my teeth in the morning.", "brush", ["brush", "eat", "sleep", "read"]),
                ("She ____ breakfast at 7 a.m.", "has", ["have", "has", "having", "had"]),
                ("We ____ to bed at night.", "go", ["go", "goes", "gone", "going"]),
                ("He ____ his face before school.", "washes", ["wash", "washes", "washed", "washing"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "reading":
            text, ans, opts = random.choice([
                ("Nam has a dog. The dog is brown. What color is Nam's dog?", "brown", ["blue", "brown", "green", "white"]),
                ("Lily goes to school at 7 o'clock. She studies English on Monday. What does Lily study on Monday?", "English", ["Math", "Science", "English", "Music"]),
                ("My house has 3 rooms. There is a kitchen and 2 bedrooms. How many bedrooms are there?", "2", ["1", "2", "3", "4"]),
                ("Mai has one brother and one sister. How many siblings does Mai have?", "2", ["1", "2", "3", "4"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "question_answer":
            text, ans, opts = random.choice([
                ("What do you say when you meet someone in the morning?", "Good morning", ["Good morning", "Good night", "Thank you", "Goodbye"]),
                ("What do you say when someone helps you?", "Thank you", ["Sorry", "Thank you", "Hello", "Good afternoon"]),
                ("What do you say before sleeping?", "Good night", ["Good morning", "Good night", "See you", "Please"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

    print(f"[english/medium] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_english_hard(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "reading_reasoning",
            "grammar_choice",
            "sentence_meaning",
            "tense_basic",
            "short_dialogue",
            "error_choice",
            "reading_inference"
        ])

        if mode == "reading_reasoning":
            text, ans, opts = random.choice([
                ("Tom has 3 books. He buys 2 more books and gives 1 book to his friend. How many books does Tom have now?", "4", ["3", "4", "5", "6"]),
                ("Lan goes to school at 7 o'clock and goes home at 4 o'clock. How many hours does she stay away from home?", "9", ["7", "8", "9", "10"]),
                ("Mai has 10 candies. She eats 2 and gives 3 to her brother. How many candies does she have left?", "5", ["4", "5", "6", "7"]),
                ("There are 12 students. 5 are boys. How many are girls?", "7", ["5", "6", "7", "8"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "grammar_choice":
            text, ans, opts = random.choice([
                ("Choose the correct sentence.", "He goes to school by bike.", ["He go to school by bike.", "He goes to school by bike.", "He going to school by bike.", "He are go to school by bike."]),
                ("Choose the correct sentence.", "My friends are playing football.", ["My friends is playing football.", "My friends are playing football.", "My friends am playing football.", "My friends playing football are."]),
                ("Choose the correct sentence.", "She does her homework after dinner.", ["She do her homework after dinner.", "She does her homework after dinner.", "She doing her homework after dinner.", "She done her homework after dinner."]),
                ("Choose the correct sentence.", "We visit our grandparents on Sunday.", ["We visits our grandparents on Sunday.", "We visit our grandparents on Sunday.", "We visited our grandparents on Sunday every week.", "We visiting our grandparents on Sunday."]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "sentence_meaning":
            text, ans, opts = random.choice([
                ("What does 'I am hungry' mean?", "Tôi đang đói.", ["Tôi đang đói.", "Tôi đang mệt.", "Tôi đang vui.", "Tôi đang ngủ."]),
                ("What does 'She is reading a book' mean?", "Cô ấy đang đọc sách.", ["Cô ấy đang chơi.", "Cô ấy đang đọc sách.", "Cô ấy đang ngủ.", "Cô ấy đang viết."]),
                ("What does 'They are in the garden' mean?", "Họ đang ở trong vườn.", ["Họ đang ở trong lớp.", "Họ đang ở trong vườn.", "Họ đang ở nhà bếp.", "Họ đang ở trường."]),
                ("What does 'My father is cooking dinner' mean?", "Bố tôi đang nấu bữa tối.", ["Bố tôi đang ngủ.", "Bố tôi đang nấu bữa tối.", "Bố tôi đang lái xe.", "Bố tôi đang đọc sách."]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "tense_basic":
            text, ans, opts = random.choice([
                ("Yesterday, I ____ to the park.", "went", ["go", "went", "goes", "going"]),
                ("Every day, she ____ milk.", "drinks", ["drink", "drinks", "drank", "drinking"]),
                ("Now, they ____ football.", "are playing", ["play", "plays", "are playing", "played"]),
                ("Last night, we ____ TV.", "watched", ["watch", "watched", "watches", "watching"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "short_dialogue":
            text, ans, opts = random.choice([
                ("A: How are you? B: I am ____.", "fine", ["fine", "book", "school", "chair"]),
                ("A: What is your name? B: ____.", "My name is Nam", ["My name is Nam", "I am ten", "I go to school", "It is blue"]),
                ("A: Where do you live? B: ____.", "I live in Ha Noi", ["I live in Ha Noi", "I am nine", "I like apples", "I am happy"]),
                ("A: How old are you? B: ____.", "I am ten years old", ["I am ten years old", "I am in class 4", "I like milk", "I have a dog"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "error_choice":
            text, ans, opts = random.choice([
                ("Which sentence has an error?", "She go to school every day.", ["I am a student.", "She go to school every day.", "They are friends.", "We play football."]),
                ("Which sentence has an error?", "He are my brother.", ["My mother is a teacher.", "He are my brother.", "The cat is under the chair.", "Lan likes music."]),
                ("Which sentence has an error?", "They is in the classroom.", ["I have a new bag.", "She reads books.", "They is in the classroom.", "We like English."]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "reading_inference":
            text, ans, opts = random.choice([
                ("John wears a raincoat and takes an umbrella. What is the weather like?", "It is rainy.", ["It is sunny.", "It is rainy.", "It is windy.", "It is snowy."]),
                ("Lily is carrying books and a ruler. Where is she probably going?", "To school", ["To school", "To the zoo", "To the beach", "To the market"]),
                ("The lights are off and everyone is sleeping. What time is it most likely?", "At night", ["In the morning", "At noon", "At night", "In the afternoon"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

    print(f"[english/hard] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


# =========================================================
# VIETNAMESE DATA
# =========================================================

VIET_ANTONYMS = [
    ("cao", "thấp"),
    ("nhanh", "chậm"),
    ("to", "nhỏ"),
    ("xa", "gần"),
    ("vui", "buồn"),
    ("sáng", "tối"),
    ("mạnh", "yếu"),
    ("siêng năng", "lười biếng"),
    ("rộng", "hẹp"),
    ("ấm", "lạnh"),
]

VIET_POS = [
    ("bàn", "danh từ"),
    ("ghế", "danh từ"),
    ("học", "động từ"),
    ("chạy", "động từ"),
    ("đẹp", "tính từ"),
    ("cao", "tính từ"),
    ("viết", "động từ"),
    ("mềm", "tính từ"),
]

VIET_SYNONYMS = [
    ("vui vẻ", "hạnh phúc"),
    ("to lớn", "khổng lồ"),
    ("siêng năng", "chăm chỉ"),
    ("gan dạ", "dũng cảm"),
    ("nhanh nhẹn", "lanh lợi"),
    ("hiền lành", "dịu dàng"),
]


# =========================================================
# VIETNAMESE
# =========================================================

def generate_vietnamese_easy(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "antonym",
            "spelling",
            "meaning",
            "synonym",
            "sentence_word",
            "simple_sentence_meaning"
        ])

        if mode == "antonym":
            word, ans = random.choice(VIET_ANTONYMS)
            wrongs = [x[1] for x in sample_distinct(VIET_ANTONYMS, 8) if x[1] != ans]
            text = f'Trái nghĩa của "{word}" là gì?'
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "spelling":
            text, ans, opts = random.choice([
                ("Từ nào viết đúng?", "sum họp", ["sum họp", "xum họp", "xung họp", "sung họp"]),
                ("Từ nào viết đúng?", "chăm chỉ", ["chăm chỉ", "trăm chỉ", "chăm chĩ", "trăm chĩ"]),
                ("Từ nào viết đúng?", "sạch sẽ", ["sạch sẽ", "sạch sẻ", "xạch sẽ", "sạch xẽ"]),
                ("Từ nào viết đúng?", "nghỉ ngơi", ["nghỉ ngơi", "ngỉ ngơi", "nghĩ ngơi", "nghỉ ngơii"]),
                ("Từ nào viết đúng?", "gọn gàng", ["gọn gàng", "gọn gàn", "gọn gằng", "gọn gan"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "meaning":
            text, ans, opts = random.choice([
                ("Từ “dũng cảm” có nghĩa là gì?", "gan dạ", ["gan dạ", "nhút nhát", "buồn bã", "lười biếng"]),
                ("Từ “siêng năng” có nghĩa là gì?", "chăm chỉ", ["chăm chỉ", "lười biếng", "ồn ào", "vui vẻ"]),
                ("Từ “lễ phép” có nghĩa là gì?", "biết cư xử đúng mực", ["biết cư xử đúng mực", "hay gây ồn", "lười học", "chạy nhanh"]),
                ("Từ “đoàn kết” có nghĩa là gì?", "cùng nhau gắn bó", ["cùng nhau gắn bó", "hay cãi nhau", "chạy thật nhanh", "im lặng"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "synonym":
            word, ans = random.choice(VIET_SYNONYMS)
            wrongs = [x[1] for x in sample_distinct(VIET_SYNONYMS, 8) if x[1] != ans]
            text = f'Từ gần nghĩa với "{word}" là gì?'
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "sentence_word":
            text, ans, opts = random.choice([
                ('Điền từ thích hợp: “Em rất ____ học bài.”', "chăm", ["chăm", "lười", "ồn", "xa"]),
                ('Điền từ thích hợp: “Bạn Nam rất ____ phép.”', "lễ", ["lễ", "chạy", "bay", "lớn"]),
                ('Điền từ thích hợp: “Buổi sáng, em ____ răng.”', "đánh", ["đánh", "ăn", "mở", "gọi"]),
                ('Điền từ thích hợp: “Cả lớp cần ____ kết với nhau.”', "đoàn", ["đoàn", "vui", "mở", "bay"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "simple_sentence_meaning":
            text, ans, opts = random.choice([
                ('Trong câu "Bạn nhỏ rất lễ phép.", từ nào nói về tính cách?', "lễ phép", ["bạn nhỏ", "rất", "lễ phép", "tính cách"]),
                ('Trong câu "Bầu trời hôm nay rất xanh.", từ nào chỉ màu sắc?', "xanh", ["bầu trời", "hôm nay", "rất", "xanh"]),
                ('Trong câu "Nam chạy rất nhanh.", từ nào chỉ hoạt động?', "chạy", ["Nam", "chạy", "rất", "nhanh"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

    print(f"[vietnamese/easy] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_vietnamese_medium(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "pos",
            "sentence",
            "meaning",
            "synonym",
            "word_class_in_sentence",
            "punctuation",
            "context_choice"
        ])

        if mode == "pos":
            word, ans = random.choice(VIET_POS)
            opts = ["danh từ", "động từ", "tính từ", "đại từ"]
            opts = opts.copy()
            random.shuffle(opts)
            text = f'Từ "{word}" thuộc loại từ nào?'
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "sentence":
            text, ans, opts = random.choice([
                ("Câu nào viết đúng chính tả?", "Em đang học bài.", ["Em đang học bài.", "Em đang hok bài.", "Em dang học bài.", "Em đang học bai."]),
                ("Câu nào viết đúng?", "Hôm nay trời rất đẹp.", ["Hôm nay trời rất đẹp.", "Hôm nay chời rất đẹp.", "Hôm nay trời rất đep.", "Hôm nay chời rất đep."]),
                ("Câu nào viết đúng?", "Buổi sáng em đi học đúng giờ.", ["Buổi sáng em đi học đúng giờ.", "Buổi ság em đi học đúng giờ.", "Buổi sáng em đi học đúg giờ.", "Buổi sáng em di học đúng giờ."]),
                ("Câu nào viết đúng?", "Cả lớp chăm chú nghe cô giáo giảng bài.", ["Cả lớp chăm chú nghe cô giáo giảng bài.", "Cả lớp trăm chú nghe cô giáo giảng bài.", "Cả lớp chăm chú nghe cô giáo giãn bài.", "Cả lớp chăm chú nge cô giáo giảng bài."]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "meaning":
            text, ans, opts = random.choice([
                ("Từ nào gần nghĩa với “vui vẻ”?", "hạnh phúc", ["hạnh phúc", "buồn bã", "tức giận", "mệt mỏi"]),
                ("Từ nào gần nghĩa với “to lớn”?", "khổng lồ", ["khổng lồ", "nhỏ bé", "yếu ớt", "lẹ làng"]),
                ("Từ nào gần nghĩa với “gan dạ”?", "dũng cảm", ["dũng cảm", "nhút nhát", "mệt mỏi", "chậm chạp"]),
                ("Từ nào gần nghĩa với “nhanh nhẹn”?", "lanh lợi", ["lanh lợi", "lười biếng", "chậm chạp", "ồn ào"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "synonym":
            word, ans = random.choice(VIET_SYNONYMS)
            wrongs = [x[1] for x in sample_distinct(VIET_SYNONYMS, 8) if x[1] != ans]
            text = f'Từ gần nghĩa với "{word}" là gì?'
            _, qid = add_question(pool, qid, text, unique_options(ans, wrongs), ans)

        elif mode == "word_class_in_sentence":
            text, ans, opts = random.choice([
                ('Trong câu "Em chạy rất nhanh.", từ "chạy" là loại từ nào?', "động từ", ["danh từ", "động từ", "tính từ", "đại từ"]),
                ('Trong câu "Bông hoa rất đẹp.", từ "đẹp" là loại từ nào?', "tính từ", ["danh từ", "động từ", "tính từ", "đại từ"]),
                ('Trong câu "Chiếc bàn này rất mới.", từ "bàn" là loại từ nào?', "danh từ", ["danh từ", "động từ", "tính từ", "đại từ"]),
                ('Trong câu "Bạn ấy viết bài rất cẩn thận.", từ "viết" là loại từ nào?', "động từ", ["danh từ", "động từ", "tính từ", "đại từ"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "punctuation":
            text, ans, opts = random.choice([
                ("Dấu câu thích hợp: “Hôm nay em đi học ____”", ".", [".", ",", "?", "!"]),
                ("Dấu câu thích hợp: “Bạn tên là gì ____”", "?", [".", ",", "?", "!"]),
                ("Dấu câu thích hợp: “Ôi, đẹp quá ____”", "!", [".", ",", "?", "!"]),
                ("Dấu câu thích hợp: “Mẹ ơi, con làm xong rồi ____”", "!", [".", ",", "?", "!"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "context_choice":
            text, ans, opts = random.choice([
                ('Từ nào phù hợp trong câu: “Bạn nhỏ rất ____ nên luôn giúp đỡ mọi người.”', "tốt bụng", ["tốt bụng", "ồn ào", "lười biếng", "chậm chạp"]),
                ('Từ nào phù hợp trong câu: “Sân trường giờ ra chơi rất ____.”', "nhộn nhịp", ["nhộn nhịp", "yên ắng", "u tối", "hẹp"]),
                ('Từ nào phù hợp trong câu: “Con suối chảy rất ____.”', "êm đềm", ["êm đềm", "gồ ghề", "nặng nề", "cứng cáp"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

    print(f"[vietnamese/medium] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


def generate_vietnamese_hard(start_id, count):
    pool = []
    qid = start_id
    attempts = 0
    max_attempts = max(count * 80, 8000)

    while can_continue(pool, count, attempts, max_attempts):
        attempts += 1
        mode = random.choice([
            "reading",
            "sentence_fix",
            "word_use",
            "main_idea",
            "choose_better_sentence",
            "context_word",
            "short_inference"
        ])

        if mode == "reading":
            text = "Đọc câu: “Lan rất chăm chỉ nên bạn luôn hoàn thành bài tập đúng giờ.” Từ nào cho biết tính cách của Lan?"
            ans = "chăm chỉ"
            opts = ["Lan", "đúng giờ", "chăm chỉ", "bài tập"]
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "sentence_fix":
            text, ans, opts = random.choice([
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
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "word_use":
            text, ans, opts = random.choice([
                ('Từ nào dùng đúng trong câu: “Bạn Nam rất ____ nên ai cũng quý.”', "lễ phép", ["lễ phép", "ồn ào", "cẩu thả", "chậm chạp"]),
                ('Điền từ thích hợp: “Em luôn ____ bài trước khi đến lớp.”', "chuẩn bị", ["chuẩn bị", "vứt", "quên", "bỏ"]),
                ('Từ nào hợp nghĩa trong câu: “Bạn ấy rất ____ nên học bài rất chăm.”', "siêng năng", ["siêng năng", "ồn ào", "lười biếng", "nóng nảy"]),
                ('Từ nào hợp nghĩa trong câu: “Chú bộ đội rất ____ khi làm nhiệm vụ.”', "dũng cảm", ["dũng cảm", "nhút nhát", "uể oải", "buồn bã"]),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "main_idea":
            text, ans, opts = random.choice([
                (
                    "Đọc đoạn: “Buổi sáng, sân trường rộn ràng tiếng cười nói. Các bạn học sinh vui vẻ bước vào lớp.” Ý chính của đoạn là gì?",
                    "Khung cảnh sân trường buổi sáng.",
                    [
                        "Khung cảnh sân trường buổi sáng.",
                        "Một buổi đi chơi xa.",
                        "Cảnh trong nhà bếp.",
                        "Một cơn mưa lớn."
                    ]
                ),
                (
                    "Đọc đoạn: “Mẹ luôn dậy sớm chuẩn bị bữa sáng cho cả nhà. Mẹ chăm lo từng việc nhỏ.” Ý chính của đoạn là gì?",
                    "Sự chăm chỉ và yêu thương của mẹ.",
                    [
                        "Sự chăm chỉ và yêu thương của mẹ.",
                        "Câu chuyện về trường học.",
                        "Một chuyến du lịch vui vẻ.",
                        "Một trận đá bóng."
                    ]
                ),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "choose_better_sentence":
            text, ans, opts = random.choice([
                (
                    "Câu nào diễn đạt hay và đúng hơn?",
                    "Những tia nắng sớm nhẹ nhàng chiếu xuống sân trường.",
                    [
                        "Những tia nắng sớm nhẹ nhàng chiếu xuống sân trường.",
                        "Nắng chiếu xuống.",
                        "Sân trường có nắng.",
                        "Nắng ở trường."
                    ]
                ),
                (
                    "Câu nào diễn đạt rõ nghĩa hơn?",
                    "Em chăm chỉ luyện viết mỗi ngày nên chữ viết ngày càng đẹp.",
                    [
                        "Em chăm chỉ luyện viết mỗi ngày nên chữ viết ngày càng đẹp.",
                        "Em viết nên đẹp.",
                        "Ngày nào em cũng đẹp chữ.",
                        "Chữ viết em mỗi ngày."
                    ]
                ),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "context_word":
            text, ans, opts = random.choice([
                (
                    'Trong câu “Bạn nhỏ cất tiếng hát trong trẻo.”, từ “trong trẻo” miêu tả điều gì?',
                    "Giọng hát",
                    ["Giọng hát", "Trang phục", "Bầu trời", "Mái tóc"]
                ),
                (
                    'Trong câu “Con đường làng quanh co dưới ánh nắng chiều.”, từ “quanh co” miêu tả điều gì?',
                    "Con đường",
                    ["Con đường", "Ánh nắng", "Bầu trời", "Ngôi nhà"]
                ),
                (
                    'Trong câu “Mặt hồ phẳng lặng như gương.”, từ “phẳng lặng” miêu tả điều gì?',
                    "Mặt hồ",
                    ["Mặt hồ", "Ánh nắng", "Bầu trời", "Hàng cây"]
                ),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

        elif mode == "short_inference":
            text, ans, opts = random.choice([
                (
                    "Đọc câu: “Bầu trời đen kịt, gió thổi mạnh, mây kéo đến rất nhanh.” Điều gì có thể sắp xảy ra?",
                    "Trời sắp mưa.",
                    ["Trời sắp mưa.", "Trời rất nắng.", "Trời sắp tối hẳn.", "Trời rất lạnh."]
                ),
                (
                    "Đọc câu: “Bé Na mang theo cặp sách, bút chì và vở.” Bé Na có thể đang đi đâu?",
                    "Bé đang đi học.",
                    ["Bé đang đi học.", "Bé đang đi chợ.", "Bé đang đi bơi.", "Bé đang đi ngủ."]
                ),
                (
                    "Đọc câu: “Bạn nhỏ khoác áo mưa và cầm ô trước khi ra ngoài.” Thời tiết lúc đó như thế nào?",
                    "Trời đang mưa.",
                    ["Trời đang mưa.", "Trời rất nóng.", "Trời có tuyết.", "Trời quang mây."]
                ),
            ])
            opts = opts.copy()
            random.shuffle(opts)
            _, qid = add_question(pool, qid, text, opts, ans)

    print(f"[vietnamese/hard] requested={count}, generated={len(pool)}, attempts={attempts}")
    return pool, qid


# =========================================================
# BUILD DATABASE
# =========================================================

def build_database(
    math_easy_count,
    math_medium_count,
    math_hard_count,
    english_easy_count,
    english_medium_count,
    english_hard_count,
    vietnamese_easy_count,
    vietnamese_medium_count,
    vietnamese_hard_count
):
    global SEEN_KEYS
    SEEN_KEYS = set()

    qid = 1

    math_easy, qid = generate_math_easy(qid, math_easy_count)
    math_medium, qid = generate_math_medium(qid, math_medium_count)
    math_hard, qid = generate_math_hard(qid, math_hard_count)

    english_easy, qid = generate_english_easy(qid, english_easy_count)
    english_medium, qid = generate_english_medium(qid, english_medium_count)
    english_hard, qid = generate_english_hard(qid, english_hard_count)

    vietnamese_easy, qid = generate_vietnamese_easy(qid, vietnamese_easy_count)
    vietnamese_medium, qid = generate_vietnamese_medium(qid, vietnamese_medium_count)
    vietnamese_hard, qid = generate_vietnamese_hard(qid, vietnamese_hard_count)

    return {
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


def count_total_questions(db):
    total = 0
    for subject in db.values():
        for level in subject.values():
            total += len(level)
    return total


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Bee Learning question bank")

    parser.add_argument("--math-easy", type=int, default=500)
    parser.add_argument("--math-medium", type=int, default=500)
    parser.add_argument("--math-hard", type=int, default=500)

    parser.add_argument("--english-easy", type=int, default=250)
    parser.add_argument("--english-medium", type=int, default=250)
    parser.add_argument("--english-hard", type=int, default=250)

    parser.add_argument("--vietnamese-easy", type=int, default=250)
    parser.add_argument("--vietnamese-medium", type=int, default=250)
    parser.add_argument("--vietnamese-hard", type=int, default=250)

    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE))
    return parser.parse_args()


def main():
    args = parse_args()

    db = build_database(
        math_easy_count=args.math_easy,
        math_medium_count=args.math_medium,
        math_hard_count=args.math_hard,
        english_easy_count=args.english_easy,
        english_medium_count=args.english_medium,
        english_hard_count=args.english_hard,
        vietnamese_easy_count=args.vietnamese_easy,
        vietnamese_medium_count=args.vietnamese_medium,
        vietnamese_hard_count=args.vietnamese_hard,
    )

    output_path = Path(args.output)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    total = count_total_questions(db)

    print(f"\nGenerated {total} questions into {output_path}")
    print("By subject:")
    for subject_name, subject_data in db.items():
        subject_total = sum(len(items) for items in subject_data.values())
        print(f"  - {subject_name}: {subject_total}")
        for level_name, items in subject_data.items():
            print(f"      {level_name}: {len(items)}")


if __name__ == "__main__":
    main()