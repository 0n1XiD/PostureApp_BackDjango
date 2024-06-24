import datetime
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from user.models import Client

MOSCOW_TZ = pytz.timezone("Europe/Moscow")


def delete_archive_clients():
    begin = (datetime.datetime.now(MOSCOW_TZ) - datetime.timedelta(minutes=5)).strftime("%H:%M")
    end = datetime.datetime.now(MOSCOW_TZ).strftime("%H:%M")
    this_year = datetime.now().year
    this_month = datetime.now().month
    this_day = datetime.now().day
    for client in Client.objects.filter(in_archive=True):
        try:
            archive_year = client.archive_date.year
            archive_month = client.archive_date.month
            archive_day = client.archive_date.day
            if archive_year < this_year and archive_month < this_month and archive_day < this_day:
                client.dalete()
        except Exception:
            pass


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_archive_clients, 'interval', weeks=4)
    scheduler.start()
