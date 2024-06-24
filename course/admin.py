import os

from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Exercise, ExerciseParse, ExerciseCode, WeekOrder, Week, WeekParse
from .services import parse_json_to_exercise, parse_week_exercise


@admin.register(Exercise)
class ExerciseAdmin(TranslatableAdmin, admin.ModelAdmin):
    list_display = ("id", 'name')
    list_display_links = ("id", 'name')
    search_fields = ("id", 'translations__name', "search_name")
    fieldsets = (
        ('Main Settings', {"fields": (
            'name',
            'description',
            'search_name',
            'have_duration', 'have_sets',
            'sets', 'repeats', 'duration',
            'alternative_exercises'
        )}),
        ('Files', {"fields": (
            'video',
            'photo1',
            'photo2'
        )})
    )
    save_on_top = True


@admin.register(ExerciseCode)
class ExerciseCodeAdmin(admin.ModelAdmin):
    list_display = ("id", 'name', 'code')
    list_display_links = ("id", 'name', 'code')
    search_fields = ("id", 'name', 'code')
    fields = ('name', 'code')


class ExerciseWeekOrderInline(admin.TabularInline):
    model = WeekOrder
    extra = 1


@admin.register(Week)
class ExerciseWeekAdmin(admin.ModelAdmin):
    list_display = ("id", 'name', 'code')
    list_display_links = ("id", 'name', 'code')
    search_fields = ("id", 'name', 'code')
    fields = ('name', 'code')
    inlines = [ExerciseWeekOrderInline]
    list_filter = (
        'code',
        'name'
    )


@admin.register(ExerciseParse)
class ExerciseParseAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        parse_json_to_exercise(obj.file.url[1:])
        os.remove(obj.file.url[1:])
        obj.delete()

@admin.register(WeekParse)
class WeekParseAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        parse_week_exercise(obj.file.url[1:])
        os.remove(obj.file.url[1:])
        obj.delete()


