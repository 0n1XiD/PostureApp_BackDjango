from django.urls import path

from .views import GetAllRates, GetRate

urlpatterns = [
    path('get-all-rates/', GetAllRates.as_view(), name='get_all_rates'),
    path('get-rate/', GetRate.as_view(), name='get_rate'),
]
