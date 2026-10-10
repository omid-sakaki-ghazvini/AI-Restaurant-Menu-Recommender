"""
سرویس ارتباط با Ollama برای دریافت پیشنهاد غذا.

این ماژول با هر دو endpoint زیر کار می‌کند:
- /api/chat     (نسخه‌های جدید Ollama)
- /api/generate (نسخه‌های قدیمی‌تر Ollama)

اگر chat در دسترس نباشد، خودکار به generate سوییچ می‌کند.
"""

import json
import re
import requests


# ============================================================
# تنظیمات
# ============================================================

OLLAMA_HOST = "http://localhost:11434"

CHAT_URL = f"{OLLAMA_HOST}/api/chat"
GENERATE_URL = f"{OLLAMA_HOST}/api/generate"
TAGS_URL = f"{OLLAMA_HOST}/api/tags"

# نام مدل دانلود شده از ModelScope
MODEL_NAME = "modelscope.cn/Qwen/Qwen2.5-7B-Instruct-GGUF:latest"

TIMEOUT_SECONDS = 300
TEMPERATURE = 0.3
TOP_P = 0.9


# ============================================================
# بررسی سلامت Ollama
# ============================================================

def check_ollama_status():
    """
    بررسی می‌کند Ollama در دسترس است و لیست مدل‌های نصب‌شده را برمی‌گرداند.
    خروجی: (bool, list)
    """
    try:
        response = requests.get(TAGS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except requests.exceptions.RequestException:
        pass

    return False, []


def is_model_available(model_name=MODEL_NAME):
    """بررسی می‌کند آیا مدل مورد نظر در Ollama نصب است یا نه."""
    ok, models = check_ollama_status()
    if not ok:
        return False

    # تطبیق دقیق یا تطبیق نام پایه (بدون تگ)
    base_name = model_name.split(":")[0]
    for m in models:
        if m == model_name:
            return True
        if m.startswith(base_name + ":"):
            return True

    return False


# ============================================================
# ساخت Prompt
# ============================================================

def build_menu_context(menu_items):
    """منو را به فرمت متنی قابل فهم برای LLM تبدیل می‌کند."""
    lines = []
    for item in menu_items:
        lines.append(
            f"- ID:{item.id} | {item.name} | "
            f"دسته: {item.get_category_display()} | "
            f"قیمت: {item.price} تومان | "
            f"مواد: {item.ingredients} | "
            f"برچسب‌ها: {item.tags} | "
            f"توضیح: {item.description}"
        )
    return "\n".join(lines)


def build_prompt(user_request, menu_context):
    """پرامپت ساختارمند می‌سازد."""
    return f"""تو یک دستیار هوشمند منوی کافه‌رستوران هستی.
وظیفه‌ی تو این است که بر اساس درخواست مشتری، از بین آیتم‌های موجود در منو،
2 تا 3 مورد را پیشنهاد دهی و دلیل انتخاب را توضیح دهی.

قوانین مهم:
1. فقط از آیتم‌هایی که در لیست منو هستند پیشنهاد بده. چیزی از خودت اضافه نکن.
2. اگر درخواست مشتری با هیچ آیتمی مطابقت نداشت، صادقانه بگو که مورد مناسبی پیدا نشد.
3. پاسخ را فقط به فرمت JSON معتبر بده، بدون متن اضافی.

فرمت پاسخ:
{{
  "recommendations": [
    {{
      "id": 1,
      "name": "نام غذا",
      "reason": "دلیل انتخاب",
      "confidence": 0.95
    }}
  ],
  "note": "توضیح کوتاه در صورت نیاز"
}}

--- منو ---
{menu_context}

--- درخواست مشتری ---
"{user_request}"

--- پاسخ JSON ---"""


# ============================================================
# استخراج JSON
# ============================================================

def extract_json(text):
    """
    JSON را از پاسخ LLM استخراج می‌کند.
    حتی اگر مدل داخل ```json بگذارد یا متن اضافی بنویسد.
    """
    if not text:
        raise ValueError("Empty response")

    # حذف بلوک‌های markdown
    text = re.sub(r"```(?:json)?", "", text).strip()
    text = text.replace("```", "").strip()

    # پیدا کردن اولین { و آخرین }
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")

    json_str = text[start:end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


# ============================================================
# فراخوانی Ollama
# ============================================================

def _call_chat_api(prompt):
    """تلاش برای فراخوانی /api/chat. اگر 404 داد، None برمی‌گرداند."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        }
    }

    try:
        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            "Ollama در دسترس نیست. مطمئن شوید سرویس Ollama در حال اجراست."
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError("پاسخ Ollama طول کشید. دوباره تلاش کنید.") from e

    # اگر endpoint پشتیبانی نمی‌شود → 404
    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")


def _call_generate_api(prompt):
    """فراخوانی /api/generate (endpoint قدیمی)."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        }
    }

    try:
        response = requests.post(
            GENERATE_URL,
            json=payload,
            timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            "Ollama در دسترس نیست. مطمئن شوید سرویس Ollama در حال اجراست."
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError("پاسخ Ollama طول کشید. دوباره تلاش کنید.") from e

    data = response.json()
    return data.get("response", "")


def call_ollama(prompt):
    """
    ابتدا /api/chat را امتحان می‌کند. اگر 404 داد (نسخه قدیمی)،
    به /api/generate سوییچ می‌کند.
    """
    # تلاش اول: /api/chat
    content = _call_chat_api(prompt)

    if content is not None:
        return content

    # تلاش دوم: /api/generate
    return _call_generate_api(prompt)


# ============================================================
# تابع اصلی
# ============================================================

def get_recommendations(user_request, menu_items):
    """
    درخواست کاربر را به Ollama می‌فرستد و پیشنهادات را برمی‌گرداند.

    پارامترها:
        user_request (str): توضیح مشتری
        menu_items (list): لیست اشیاء MenuItem

    خروجی:
        dict: {"recommendations": [...], "note": "..."}
    """
    if not menu_items:
        return {"recommendations": [], "note": "منو خالی است."}

    # 1. ساخت context و prompt
    menu_context = build_menu_context(menu_items)
    prompt = build_prompt(user_request, menu_context)

    # 2. فراخوانی Ollama
    raw_content = call_ollama(prompt)

    # 3. تجزیه JSON
    try:
        result = extract_json(raw_content)
    except (ValueError, json.JSONDecodeError) as e:
        return {
            "recommendations": [],
            "note": f"پاسخ مدل قابل تجزیه نبود: {str(e)} | متن: {raw_content[:300]}"
        }

    # 4. اعتبارسنجی ساختار
    if "recommendations" not in result:
        return {
            "recommendations": [],
            "note": "ساختار پاسخ نامعتبر است."
        }

    if not isinstance(result["recommendations"], list):
        return {
            "recommendations": [],
            "note": "فیلد recommendations باید یک لیست باشد."
        }

    return result