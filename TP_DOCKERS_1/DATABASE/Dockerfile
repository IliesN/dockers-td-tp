FROM postgres:17.2-alpine

#not secure
#ENV POSTGRES_DB=db \
#   POSTGRES_USER=usr \
#   POSTGRES_PASSWORD=pwd


COPY sql/ /docker-entrypoint-initdb.d/
