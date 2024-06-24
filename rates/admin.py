from django.contrib import admin

from .models import Rate


@admin.register(Rate)
class ExerciseWeekAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main Settings', {"fields": (
            "title",
            'description',
            'days_count'
        )}),
    )
    list_display = ("title", 'days_count',)
    list_display_links = ("title", 'days_count')
    search_fields = ("title", 'description')
    save_on_top = True
