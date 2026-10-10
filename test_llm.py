"""
تست ساده‌ی Ollama با متن فارسی درست.
"""
import requests

MODEL_NAME = "modelscope.cn/Qwen/Qwen2.5-7B-Instruct-GGUF"

prompt = "سلام، یک غذای سبک و گیاهی پیشنهاد بده. کوتاه جواب بده."

payload = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.3,
    }
}

print("در حال ارسال به Ollama...")
response = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=180
)

if response.status_code == 200:
    data = response.json()
    print("\n=== پاسخ مدل ===\n")
    print(data.get("response", "پاسخی نیامد"))
else:
    print(f"خطا: {response.status_code}")
    print(response.text)