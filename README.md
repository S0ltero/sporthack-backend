# SportHack

**ENG:** Tracker of sports events for sports sections in an educational institution

**Funtionality:**

* **Trainers**
  * Create and plan trainings and events for your section
  * Track the activity of students in their sections
* **Students**
  * Sign up for trainings by QR code
  * Follow the schedule of training and events
  * Track your statistics and ranking among other students

---

**RUS:** Трекер спортивных мероприятия для спортивных секций в учебном заведении

**Функционал:**

* **Тренеры**
  * Создавать и планировать тренировки и мероприятия своих секций
  * Отслеживать активность студентов в своих секциях
* Студенты
  * Записываться на тренировки с помощью QR кода
  * Следить за расписанием тренировок и мероприятий
  * Отслеживать свою статистику и рейтинг среди других студентов

## Requirements

Python 3.7+
DB: Postgres

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
