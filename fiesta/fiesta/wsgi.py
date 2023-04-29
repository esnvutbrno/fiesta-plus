"""
WSGI config for fiesta project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""
from __future__ import annotations

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
