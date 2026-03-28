"""
WSGI config for kck_api project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kck_api.settings.base")

application = get_wsgi_application()
