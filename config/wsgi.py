"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""


import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

from django.conf import settings

os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

for p in ["pdf_preview", "docs", "qr", "docs_qr", "pdf_preview_qr"]:
    os.makedirs(os.path.join(settings.MEDIA_ROOT, p), exist_ok=True)
