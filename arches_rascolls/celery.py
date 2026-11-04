from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_before_create_process
from django.db import connections

import platform

if platform.system().lower() == "windows":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arches_rascolls.settings")
app = Celery("arches_rascolls")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_before_create_process.connect
def close_db_pools_before_fork(**kwargs):
    # Celery's Django fixup opens the pool in the parent; children must not share it.
    for connection in connections.all():
        connection.close_pool()
