FROM alpine:latest

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_ADMIN_USER
ARG POSTGRES_ADMIN_PASSWORD
ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_DB

RUN apk update && apk add --no-cache postgresql postgresql-contrib

RUN mkdir -p /var/lib/postgresql/data /run/postgresql

RUN chown -R postgres:postgres /var/lib/postgresql /run/postgresql

COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh

USER postgres

RUN initdb -D /var/lib/postgresql/data

RUN /docker-entrypoint-initdb.d/init.sh

CMD ["postgres", "-D", "/var/lib/postgresql/data"]