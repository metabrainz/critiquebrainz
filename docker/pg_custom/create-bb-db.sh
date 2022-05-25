#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER bookbrainz;
	CREATE DATABASE bookbrainz;
	GRANT ALL PRIVILEGES ON DATABASE bookbrainz TO bookbrainz;
EOSQL