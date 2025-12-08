FROM php:8.3-fpm

# Устанавливаем зависимости для pdo_pgsql
RUN apt-get update && apt-get install -y \
        libpq-dev \
        postgresql-client \
    && docker-php-ext-install pdo pdo_pgsql
