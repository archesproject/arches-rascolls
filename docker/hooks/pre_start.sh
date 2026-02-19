#!/bin/bash
# Rascolls pre-start hook

${WEB_ROOT}/ENV/bin/python manage.py db_index reindex_database
