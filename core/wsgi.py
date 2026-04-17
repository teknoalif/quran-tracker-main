import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quran_tracker.settings')
from django.core.management import call_command
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f'Migration failed: {e}')
from django.core.management import call_command
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f'Migration failed: {e}')
application = get_wsgi_application()

try:
    from django.contrib.auth.models import User
    if not User.objects.filter(username='alif').exists():
        User.objects.create_superuser('alif', 'admin@kakalif.my.id', 'alif')
    users = ['nurmawan', 'reza', 'agung', 'priyo', 'umar', 'rifqi']
    for u in users:
        if not User.objects.filter(username=u).exists():
            User.objects.create_user(username=u, password=u)
except Exception:
    pass

app = application
