# Установка

## Системные требования
Python 3.7+
База данных: Postgres

## Environments

Create file `.env`

Provide in file this values:

```
SITE_DOMAIN=host.docker.internal

DJANGO_SECRET_KEY=
DJANGO_DEBUG=

CORS_ORIGIN_ALLOW_ALL=
CORS_ORIGIN_WHITELIST=                        # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect

DB_NAME=
DB_USER=
DB_HOST=                                      # If used local database use this value `host.docker.internal`
DB_PASSWORD=
DB_PORT=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_USER=
EMAIL_PASSWORD=
```

## Настройка Django

* Создадим миграции: `docker-compose run --rm -u 0 web python manage.py makemigrations`

* Применим миграции к базе данных: `docker-compose run --rm -u 0 web python manage.py migrate`

