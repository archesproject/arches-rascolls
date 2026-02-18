#!/bin/bash
# Rascolls post-reindex hook: arches-search db_index

${WEB_ROOT}/ENV/bin/python manage.py db_index reindex_database
