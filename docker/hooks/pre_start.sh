#!/bin/bash
# Rascolls pre-start hook
echo ""
echo "----- *** RUNNING REPORT CONFIG LOAD *** -----"
echo ""

cd ${APP_ROOT}
${WEB_ROOT}/ENV/bin/python manage.py report_configs load