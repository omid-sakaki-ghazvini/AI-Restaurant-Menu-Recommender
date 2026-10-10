from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'is_available',
        'created_at'
    )
    list_filter = (
        'category',
        'is_available'
    )
    search_fields = (
        'name',
        'description',
        'tags',
        'ingredients'
    )
    list_editable = ('is_available',)

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('جزئیات', {
            'fields': ('ingredients', 'tags')
        }),
        ('وضعیت', {
            'fields': ('is_available',)
        }),
    )