FROM public.ecr.aws/l1p7h1f9/archesproject-fargeo:8.0.x-base-prod AS base
ENV APP_ROOT=${WEB_ROOT}/arches-rascolls
ENV ARCHES_DJANGO_DEBUG=True

WORKDIR ${WEB_ROOT}
RUN apt-get update && apt-get install nginx -y && ENV/bin/pip install gunicorn botocore boto3 django-storages psutil

RUN openssl ecparam -out /etc/ssl/private/nginx-selfsigned.key -name prime256v1 -genkey && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -key /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost"

COPY . ${WEB_ROOT}/arches-rascolls
RUN source ${WEB_ROOT}/ENV/bin/activate && cd ${APP_ROOT} && pip install .
COPY ./docker/static_frontend_configuration ${WEB_ROOT}/arches-rascolls/frontend_configuration
WORKDIR ${APP_ROOT}
RUN npm i
RUN source ../ENV/bin/activate && ls /web_root/ENV/lib/python3.12/site-packages/arches_modular_reports/media/js/reports && npm run build_production_unsafe && python3 manage.py collectstatic


FROM public.ecr.aws/l1p7h1f9/archesproject-fargeo:8.0.x-base-prod AS deploy 
USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV WEB_ROOT=/web_root
ENV APP_ROOT=${WEB_ROOT}/arches-rascolls
ENV BASE_WEB=/web_root
ENV BASE_APP=${BASE_WEB}/arches-rascolls
COPY --from=base ${BASE_APP}/arches_rascolls/staticfiles /var/www/media
COPY --from=base ${BASE_APP}/webpack/webpack-stats.json ${APP_ROOT}/webpack/webpack-stats.json
COPY --from=base /etc/ssl/private/nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY --from=base /etc/ssl/certs/nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt

RUN chgrp www-data /var/www/media -R
RUN  apt-add-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y make software-properties-common ca-certificates curl gnupg nginx vim memcached

# Root project folder
ENV WHEELS=/wheels
ENV PYTHONUNBUFFERED=1

WORKDIR ${WEB_ROOT}

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip ./aws
  
# Install the Arches application
# FIXME: ADD from github repository instead?

# From here, run commands from ARCHES_ROOT
RUN source ${WEB_ROOT}/ENV/bin/activate

COPY docker/entrypoint.sh ${WEB_ROOT}/entrypoint.sh
RUN chmod -R 700 ${WEB_ROOT}/entrypoint.sh &&\
  dos2unix ${WEB_ROOT}/entrypoint.sh

COPY . ${WEB_ROOT}/arches-rascolls

# Set default workdir
WORKDIR ${APP_ROOT}
COPY docker/nginx/default.conf /etc/nginx/sites-available/default
RUN source ${WEB_ROOT}/ENV/bin/activate && pip install . && pip install gunicorn boto boto3 django-storages psutil

# # Set entrypoint
ENTRYPOINT ["../entrypoint.sh"]
CMD ["run_gunicorn"]

# Expose port 8000
EXPOSE 8000
