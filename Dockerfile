FROM python:3.7
RUN apt update
RUN apt install -y default-mysql-client
WORKDIR /app
COPY . ./
RUN sh /app/dependencies.sh
RUN chmod +x /app/alembic_migrations.sh
#WORKDIR /app/src
#RUN sh /app/alembic_migrations.sh
#WORKDIR /app
CMD ["start.sh"]
EXPOSE 8080
