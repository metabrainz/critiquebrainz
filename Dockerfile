FROM metabrainz/python:3.8-20210115

ARG DEPLOY_ENV

RUN apt-get update \
     && apt-get install -y --no-install-recommends \
                        build-essential \
                        ca-certificates \
                        cron \
                        git \
                        libpq-dev \
                        libffi-dev \
                        libssl-dev \
                        libxml2-dev \
                        libxslt1-dev \
                        rsync \
    && rm -rf /var/lib/apt/lists/*

# PostgreSQL client
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
ENV PG_MAJOR 12
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update \
    && apt-get install -y postgresql-client-$PG_MAJOR \
    && rm -rf /var/lib/apt/lists/*
# Specifying password so that client doesn't ask scripts for it...
ENV PGPASSWORD "critiquebrainz"

# Node
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
   && apt-get install -y nodejs \
   && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uWSGI==2.0.18

RUN mkdir /code
WORKDIR /code

# Python dependencies
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Node dependencies
COPY ./package.json ./package-lock.json /code/
RUN npm install

COPY . /code/

# Build static files
RUN npm run build

# Compile translations
RUN pybabel compile -d critiquebrainz/frontend/translations

RUN useradd --create-home --shell /bin/bash critiquebrainz

############
# Services #
############

# Consul Template service is already set up with the base image.
# Just need to copy the configuration.
COPY ./docker/prod/consul-template.conf /etc/consul-template.conf

# runit service files
# All services are created with a `down` file, preventing them from starting
# rc.local removes the down file for the specific service we want to run in a container
# http://smarden.org/runit/runsv.8.html

COPY ./docker/$DEPLOY_ENV/uwsgi/uwsgi.service /etc/service/uwsgi/run
RUN chmod 755 /etc/service/uwsgi/run
COPY ./docker/$DEPLOY_ENV/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini
RUN touch /etc/service/uswgi/down

# cron jobs
ADD ./docker/prod/cron/jobs /tmp/crontab
RUN chmod 0644 /tmp/crontab && crontab -u critiquebrainz /tmp/crontab
RUN rm /tmp/crontab
RUN touch /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log \
    && chown critiquebrainz:critiquebrainz /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log
RUN touch /etc/service/cron/down

ARG GIT_COMMIT_SHA
ENV GIT_SHA ${GIT_COMMIT_SHA}

EXPOSE 13032
