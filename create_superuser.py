# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beautyofportugal.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

SUPERUSER_NAME = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL", "pjdhirajshrestha@gmail.com")
SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "changeme")

if not User.objects.filter(username=SUPERUSER_NAME).exists():
    User.objects.create_superuser(
        username=SUPERUSER_NAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD,
    )
    print(f"Superuser '{SUPERUSER_NAME}' created.")
else:
    print(f"Superuser '{SUPERUSER_NAME}' already exists.")
