import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beautyofportugal.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

SUPERUSER_NAME = "admin"
SUPERUSER_EMAIL = "admin@example.com"
SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PWD")

if not SUPERUSER_PASSWORD:
    raise ValueError("DJANGO_SUPERUSER_PWD environment variable is not set!")

if not User.objects.filter(username=SUPERUSER_NAME).exists():
    User.objects.create_superuser(
        username=SUPERUSER_NAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD,
    )
    print(f"Superuser '{SUPERUSER_NAME}' created successfully!")
else:
    user = User.objects.get(username=SUPERUSER_NAME)
    user.set_password(SUPERUSER_PASSWORD)
    user.save()
    print(f"Superuser '{SUPERUSER_NAME}' already exists. Password updated.")
