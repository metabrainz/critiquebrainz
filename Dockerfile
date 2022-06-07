FROM metabrainz/python:3.10-20220315

ENV PYTHONUNBUFFERED 1

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
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
ENV PG_MAJOR 12
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-$PG_MAJOR \
    && rm -rf /var/lib/apt/lists/*

# Specifying password so that client doesn't ask scripts for it...
ENV PGPASSWORD "critiquebrainz"

# Node
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
   && apt-get install -y nodejs \
   && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip==21.0.1

RUN pip install --no-cache-dir uWSGI==2.0.20

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

# runit service files
# All services are created with a `down` file, preventing them from starting
# rc.local removes the down file for the specific service we want to run in a container
# http://smarden.org/runit/runsv.8.html

COPY ./docker/rc.local /etc/rc.local

# UWSGI
COPY ./docker/uwsgi/consul-template-uwsgi.conf /etc/consul-template-uwsgi.conf
COPY ./docker/uwsgi/uwsgi.service /etc/service/uwsgi/run
COPY ./docker/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini
RUN touch /etc/service/uwsgi/down

# cron jobs
COPY ./docker/cron/consul-template-cron-config.conf /etc/consul-template-cron-config.conf
COPY ./docker/cron/cron-config.service /etc/service/cron-config/run
COPY ./docker/cron/crontab /etc/cron.d/critiquebrainz
RUN chmod 0644 /etc/cron.d/critiquebrainz
RUN touch /etc/service/cron/down
RUN touch /etc/service/cron-config/down

RUN touch /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log \
    && chown critiquebrainz:critiquebrainz /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log

ARG GIT_COMMIT_SHA
ENV GIT_SHA ${GIT_COMMIT_SHA}

EXPOSE 13032
