FROM metabrainz/python:3.7

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
ENV PG_MAJOR 9.5
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update \
    && apt-get install -y postgresql-client-$PG_MAJOR \
    && rm -rf /var/lib/apt/lists/*
# Specifying password so that client doesn't ask scripts for it...
ENV PGPASSWORD "critiquebrainz"

# Node
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -y nodejs

RUN pip install uWSGI==2.0.13.1

RUN mkdir /code
WORKDIR /code

# Python dependencies
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

# Node dependencies
COPY ./package.json /code/
COPY ./npm-shrinkwrap.json /code/
RUN npm install

COPY . /code/

# Build static files
RUN ./node_modules/.bin/gulp

# Compile translations
RUN pybabel compile -d critiquebrainz/frontend/translations

RUN useradd --create-home --shell /bin/bash critiquebrainz

############
# Services #
############

# Consul Template service is already set up with the base image.
# Just need to copy the configuration.
COPY ./docker/prod/consul-template.conf /etc/consul-template.conf

COPY ./docker/$DEPLOY_ENV/uwsgi/uwsgi.service /etc/service/uwsgi/run
RUN chmod 755 /etc/service/uwsgi/run
COPY ./docker/$DEPLOY_ENV/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini

# cron jobs
ADD ./docker/prod/cron/jobs /tmp/crontab
RUN chmod 0644 /tmp/crontab && crontab -u critiquebrainz /tmp/crontab
RUN rm /tmp/crontab
RUN touch /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log \
    && chown critiquebrainz:critiquebrainz /var/log/dump_backup.log /var/log/public_dump_create.log /var/log/json_dump_create.log

# Make sure the cron service doesn't start automagically
# http://smarden.org/runit/runsv.8.html
RUN touch /etc/service/cron/down

ARG GIT_COMMIT_SHA
ENV GIT_SHA ${GIT_COMMIT_SHA}

EXPOSE 13032
