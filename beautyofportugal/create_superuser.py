import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beautyofportugal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'dhiracadmin'
email = 'pjdhirajshrestha@gmail.com'
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    if password:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    else:
        print("DJANGO_SUPERUSER_PASSWORD is not set. Superuser not created.")
else:
    print(f"Superuser '{username}' already exists.")
