DB_HOSTNAME=db
DB_PORT=5432
DB_USER=bookbrainz
DB_NAME=bookbrainz
DB_PASSWORD=bookbrainz
export PGPASSWORD=$DB_PASSWORD

psql -f admin/sql/test/bb-test-data.sql -h $DB_HOSTNAME -p $DB_PORT -U $DB_USER -d $DB_NAME
