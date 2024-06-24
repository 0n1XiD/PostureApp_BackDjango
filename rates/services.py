from datetime import datetime

from .models import Rate


def get_all_rates() -> Rate:
    return Rate.objects.all()


def get_rate(rate_id: int) -> Rate:
    return Rate.objects.get(id=rate_id)
