#!/bin/sh

# Configure PostgreSQL to listen on all IP addresses
echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf

# If the database directory is empty, initialize the database
if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
    initdb -D /var/lib/postgresql/data
fi

pg_ctl -D /var/lib/postgresql/data -o "-c listen_addresses='*'" -w start

psql postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
psql postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"
psql postgres -c "CREATE USER $POSTGRES_ADMIN_USER WITH SUPERUSER PASSWORD '$POSTGRES_ADMIN_PASSWORD';"

pg_ctl -D /var/lib/postgresql/data -m fast -w stop