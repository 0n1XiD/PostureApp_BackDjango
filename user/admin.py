
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

try:
    from rest_framework.authtoken.models import TokenProxy as DRFToken
except ImportError:
    from rest_framework.authtoken.models import Token as DRFToken

from .models import Client, User, ClientCondition, ClientPosturePhotos, ClientWeek, ClientDay


class ClientConditionInline(admin.StackedInline):
    model = ClientCondition
    extra = 0


class ClientPosturePhotosInline(admin.StackedInline):
    model = ClientPosturePhotos
    extra = 0


class ClientDayInline(admin.StackedInline):
    model = ClientDay
    extra = 0


@admin.register(ClientWeek)
class ClientWeekInline(admin.ModelAdmin):
    search_fields = ('client__first_name__icontains',)
    inlines = [ClientDayInline]
    extra = 0


@admin.register(Client)
class ClientAdmin(BaseUserAdmin):
    change_list_template = "admin/model_change_list.html"

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('analysis-google-sheets/', self.analysis_xlsx)
    #     ]
    #     return custom_urls + urls
    #
    # def analysis_xlsx(self, request):
    #     analysis_google_sheets()
    #     print('ok')
    #     self.message_user(request, f"Данные в google sheets обновлены")
    #     return HttpResponseRedirect("../")

    fieldsets = (
        ('Main Info', {"fields": (
            "password",
            "email",
            ('first_name', 'last_name'),
            ('gender', 'birthday'),
            'phone',
            'last_visit',
            'avatar',
            'authorization_code',
            'is_first_login',
            'complete_day_time',
            'in_archive',
            'archive_date',
        )}),
        ('Posture Info', {"fields": (
            ('height', 'weight'),
            'posture_side', 'posture_back',
        )}),
        ('Additional', {"fields": (
            'current_week',
            'current_day',
        )}),
    )
    add_fieldsets = (
        ('Main Info', {
            "fields": (
                "password1",
                "password2",
                "email",
                ('first_name', 'last_name'),
                ('gender', 'birthday'),
                'phone',
                'is_first_login',
            )
        }),
    )
    inlines = [
        ClientConditionInline,
        ClientPosturePhotosInline,
    ]
    list_display = ("id", 'first_name', 'last_name', 'email')
    list_display_links = ("id", 'first_name', 'last_name', 'email')
    search_fields = ("id", 'first_name', 'last_name', 'email')
    readonly_fields = ('last_visit', 'complete_day_time',)
    ordering = ('email',)
    save_on_top = True

    actions = ['analysis_xlsx', 'remove_user_progress']

    def save_model(self, request, obj, form, change):
        obj.email = obj.email.lower()
        obj.save()
        super().save_model(request, obj, form, change)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('Main Info', {"fields": (
            "password",
            "email",
            ('first_name', 'last_name'),
            'status',
            'is_staff',
            'is_superuser',
            'complete_day_time'
        )}),
    )
    add_fieldsets = (
        ('Main Info', {
            "fields": (
                "password1",
                "password2",
                "email",
                ('first_name', 'last_name'),
                'status',
                'is_staff',
                'is_superuser',
            )
        }),
    )
    list_display = ("id", 'first_name', 'last_name', 'email')
    list_display_links = ("id", 'first_name', 'last_name', 'email')
    search_fields = ("id", 'first_name', 'last_name', 'email')
    ordering = ('id',)
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.email = obj.email.lower()
        obj.save()
        super().save_model(request, obj, form, change)


admin.site.unregister(DRFToken)
