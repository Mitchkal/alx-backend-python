version: '3.9'

services:
  db:
    image: mysql:8.0.42
    restart: always
    env_file:
      - .env
    environment:
      MYSQL_DB: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    ports:
      - '3306:3306'
  web:
    build: .
    command: python3 manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - '8000:8000'
    env_file:
      - .env
    depends_on:
      - db

volumes:
  db_data:
