from django.conf import settings
import datetime

def create_data(date: datetime.date) -> str:
    oy = date.month
    kun = date.day
    yil = date.year

    oy_nomi = settings.MOTH_SETTINGS[oy]
    return f"{oy_nomi} {kun}, {yil}"
