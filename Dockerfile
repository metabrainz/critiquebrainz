FROM python:3.5.1

RUN apt-get update \
    && apt-get install -y build-essential \
                          libxml2-dev \
                          libxslt1-dev \
                          libffi-dev \
                          libssl-dev

# PostgreSQL client
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
ENV PG_MAJOR 9.5
ENV PG_VERSION 9.5.3-1.pgdg80+1
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update \
    && apt-get install -y postgresql-client-$PG_MAJOR=$PG_VERSION \
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
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Node dependencies
COPY package.json /code/
COPY npm-shrinkwrap.json /code/
RUN npm install

COPY . /code/
RUN ./node_modules/.bin/gulp

CMD ["uwsgi", "docker/uwsgi.ini"]
