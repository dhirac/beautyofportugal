from pathlib import Path
import os
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------
# Database
# --------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),  # Railway provides this automatically
        conn_max_age=600,
        ssl_require=True  # Railway Postgres requires SSL
    )
}

# --------------------
# Security
# --------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-default-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    'beautyofportugal-production.up.railway.app',
    '127.0.0.1',
    'localhost'
]

CSRF_TRUSTED_ORIGINS = [
    'https://beautyofportugal-production.up.railway.app'
]

# --------------------
# Stripe Keys
# --------------------
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# --------------------
# Email
# --------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "93c4da001@smtp-brevo.com")
EMAIL_HOST_PASSWORD = os.getenv('SENDBLUE_SMTP_API_KEY')

# --------------------
# Static & Media
# --------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --------------------
# TinyMCE
# --------------------
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'plugins': 'image link media code',
    'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | link image media | code',
    'image_caption': True,
    'automatic_uploads': True,
    'file_picker_types': 'image',
    "images_upload_url": "/upload-image-tinymce/",
    "relative_urls": False,
    "remove_script_host": False,
}
