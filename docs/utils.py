from django.conf import settings

def create_data(date: str) -> str:
    
    oy, yil = map(str, date.split())
    yil = yil.replace("-yil", "")
    kun, oy = oy.split('-')
    oy = oy.replace(" ","").title()
    return f"{settings.MOTH_SETTINGS[oy]} {kun}, {yil}"