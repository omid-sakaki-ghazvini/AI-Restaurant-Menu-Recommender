from django.db import models


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'پیش‌غذا'),
        ('main', 'غذای اصلی'),
        ('dessert', 'دسر'),
        ('drink', 'نوشیدنی'),
        ('breakfast', 'صبحانه'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="نام"
    )
    description = models.TextField(
        verbose_name="توضیحات"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="دسته"
    )
    price = models.PositiveIntegerField(
        verbose_name="قیمت (تومان)"
    )
    ingredients = models.TextField(
        verbose_name="مواد اولیه",
        help_text="با کاما جدا کنید"
    )
    tags = models.CharField(
        max_length=200,
        verbose_name="برچسب‌ها",
        help_text="مثال: گیاهی، تند، سبک، بدون گلوتن"
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم‌های منو"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def ingredients_list(self):
        return [i.strip() for i in self.ingredients.split(',') if i.strip()]