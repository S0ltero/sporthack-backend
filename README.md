# Установка

## Системные требования
Python 3.7+
База данных: MySQL

## Виртуальное окружение
Переходим в папку проекта
cd `path/to/sporthack`
Чтобы создать виртуальное окружение, выполняем следующие команды:
```
python3 -m pip install --upgrade pip
pip3 install virtualenv
python3 -m venv venv
```
Активируем наше виртуальное окружение:
```source venv/bin/activate ```

Установим модули:
```pip install -r requirements.txt```

## Конфигурация
Создайте папку ```local```
В нее поместите файл ```config.json```
в ```config.json``` Запишем следующее:
```
{
    "secret_key": "",
    "database": "",
    "user": "",
    "host": "",
    "password": "",
    "port": "",

    "email_host": "",
    "email_port": ,
    "email_user": "",
    "email_password": ""
}
```

## Настройка Django

* Создадим миграции: `python manage.py makemigrations`

* Применим миграции к базе данных: `python manage.py migrate`

## CRON

В планировщик задач `CRON` необходимо добавить выполнение следующей команды:

`python manage.py updateevents` - Обновляет статус мероприятий. (Рекомендованно выполение каждые 5 минут.)

`python manage.py updatetrainings` - Обновляет статус тренировок, добавляет длительность тренировок к рейтингу участников. (Рекомендованно выполение каждые 5 минут.)