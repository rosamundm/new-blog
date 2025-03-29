from .base import *


# don't worry; these are all only used locally
DEBUG = True
SECRET_KEY = "django-insecure-#onrf*d%58loz+)io*t)ka1+0oy9rzamuv=y970)0wkq=1)&7g"
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
