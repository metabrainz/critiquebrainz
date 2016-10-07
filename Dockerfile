FROM python:3.5.2

COPY ./docker/prod/environment /etc/consul_template_env.sh

COPY ./docker/prod/docker-helpers/install_consul_template.sh \
     ./docker/prod/docker-helpers/install_runit.sh \
     /usr/local/bin/
RUN chmod 755 /usr/local/bin/install_consul_template.sh /usr/local/bin/install_runit.sh && \
    sync && \
    install_consul_template.sh && \
    rm -f \
        /usr/local/bin/install_consul_template.sh \
        /usr/local/bin/install_runit.sh

##################
# CritiqueBrainz #
##################

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
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    build-essential \
                    libffi-dev \
                    libssl-dev \
                    libxml2-dev \
                    libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

# Node dependencies
COPY ./package.json /code/
COPY ./npm-shrinkwrap.json /code/
RUN npm install

COPY . /code/

# Build static files
RUN ./node_modules/.bin/gulp

############
# Services #
############

# Consul-template is already installed with install_consul_template.sh
COPY ./docker/prod/uwsgi.service /etc/sv/uwsgi/run
RUN chmod 755 /etc/sv/uwsgi/run && \
    ln -sf /etc/sv/uwsgi /etc/service/

# Configuration
COPY ./docker/prod/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY ./docker/prod/consul-template.conf /etc/consul-template.conf

EXPOSE 13032
ENTRYPOINT ["/usr/local/bin/runsvinit"]
