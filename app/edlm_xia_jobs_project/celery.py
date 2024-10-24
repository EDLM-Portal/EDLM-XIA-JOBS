import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'edlm_xia_jobs_project.settings')

app = Celery('edlm_xia_jobs_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
