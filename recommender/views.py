from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import MenuItem
from .services.llm_service import get_recommendations, is_model_available


@require_http_methods(["GET", "POST"])
def index(request):
    """صفحه‌ی اصلی: فرم توضیحات + نمایش پیشنهادات."""
    context = {
        "user_request": "",
        "recommendations": None,
        "note": None,
        "error": None,
    }

    if request.method == "POST":
        user_request = request.POST.get("description", "").strip()
        context["user_request"] = user_request

        if not user_request:
            context["error"] = "لطفاً توضیح دهید چه چیزی می‌خواهید."
            return render(request, "recommender/index.html", context)

        # بررسی سلامت Ollama و مدل
        if not is_model_available():
            context["error"] = (
                "مدل هوش مصنوعی در دسترس نیست. "
                "لطفاً مطمئن شوید Ollama در حال اجراست و مدل دانلود شده است."
            )
            return render(request, "recommender/index.html", context)

        try:
            menu_items = list(MenuItem.objects.filter(is_available=True))
            result = get_recommendations(user_request, menu_items)

            # تطبیق idهای پیشنهادی با آیتم‌های دیتابیس
            recommendations = []
            item_map = {item.id: item for item in menu_items}

            for rec in result.get("recommendations", []):
                item_id = rec.get("id")
                item = item_map.get(item_id)
                if item:
                    recommendations.append({
                        "item": item,
                        "reason": rec.get("reason", ""),
                        "confidence": rec.get("confidence", 0),
                    })

            context["recommendations"] = recommendations
            context["note"] = result.get("note")

            if not recommendations:
                context["error"] = (
                    "متأسفانه موردی متناسب با درخواست شما پیدا نشد. "
                    "لطفاً توضیحات را تغییر دهید."
                )

        except RuntimeError as e:
            context["error"] = str(e)
        except Exception as e:
            context["error"] = f"خطای غیرمنتظره: {e}"

    return render(request, "recommender/index.html", context)