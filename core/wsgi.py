import os
from django.core.wsgi import get_wsgi_application

# PASTIKAN ini merujuk ke folder 'core' (tempat settings.py berada)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Alias untuk Vercel
app = application
