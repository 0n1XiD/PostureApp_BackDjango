from django.urls import path

from webhook.views import ClickFunnelsWebhookView

urlpatterns = [
    path('webhook/', ClickFunnelsWebhookView.as_view(), name='clickfunnels_webhook'),
]