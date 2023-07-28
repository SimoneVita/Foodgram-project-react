![Github actions](https://github.com/simonevita/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# YaMDb(API)
_________________________________________________
## Описание
База произведений с обзорами, оценками и комментариями, которая находится в контейнере.

### YaMDB - возможности:

- Просмотреть список доступных произведений
- Оставлять обзоры, ставить оценки.
- Обсуждать обзоры в комментариях
- Посмотреть рейтинг произведения, либо поделиться своим опытом.
- Обладает удобным API-интерфейсом
 
_____________________________________________________

## Техническое описание

### Примененные технологии
 > Python 3.7.9
 > Django 3.2.16
 > djangorestframework 3.12.4
 > djangorestframework-simplejwt 4.7.2
 > PyJWT 2.1.0
 > Gunicorn 20.0.4
 > Postgres 13.0
 > Nginx 1.21.3

### Проект доступен по следующей ссылке:
http://158.160.66.220/redoc/

### Как локально запустить проект:
!!!Запустить на локальной машине Docker!!!


Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/SimoneVita/yamdb_final.git
```

```
cd infra
```

Создать файл .env:
```
touch .env
```
Открыть в редакторе файл .env:
```
nano .env
```
Погрузить в файл .env следующие значения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres # установите свой пароль для подключения к базе
DB_HOST=db
DB_PORT=5432
SECRET_KEY='...' # секретный ключ, нужно установить свой
```
Закрыть файл .env с сохранием:
```
^X
```
Чтобы оставить имя без изменения нажмите enter (return для MacOS), далее
выходим в корневую директорию:
```
cd ..
```
Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```
Переход в директорию infra и запуск:
```
cd infra
```
```
docker-compose up
```
Необходимо открыть новый терминал и ввести по порядку следующие команды:
```
docker-compose exec web python manage.py makemigrations
```
```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py collectstatic --no-input
```
Создайте суперюзера:
```
docker-compose exec web python manage.py createsuperuser
```
Наполнить базу данных тестовыми данными (работает только при пустой базе данных):
```
docker-compose exec web python manage.py basefill
```

Документация к APi доступна по адресу: 
```
http://localhost/redoc/
```
Образ на Dockerhub:
```
simonevita / api_yamdb
```

## Запуск проекта на боевом сервере

Устанавливаем на сервер docker и docker-compose

Копируем на сервер файлы docker-compose.yaml и default.conf

Переходим в директорию infra и вводим команду:
```
scp docker-compose.yaml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yaml
```
далее вводим следующие команды:
```
cd nginx
scp default.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx/default.conf
```
В Secrets на Github необходимо добавить следующие переменные:
```
DB_ENGINE=django.db.backends.postgresql # указать, что проект работает с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=db # название сервиса БД (контейнера) 
DB_PORT=5432 # порт для подключения к БД
DOCKER_USERNAME= # Username на DockerHub
DOCKER_PASSWORD= # Пароль на DockerHub
HOST= # ip боевого сервера
USER= # Имя пользователя на удалённом сервере
SSH_KEY= # SSH-key компьютера (локальный ключ), с которого будет происходить подключение к удалённому серверу
PASSPHRASE= #Если для ssh используется фраза-пароль
TELEGRAM_TO= #ID пользователя в Telegram, можно узнать у @userinfobot
TELEGRAM_TOKEN= #ID бота в Telegram подскажет @BotFather
```

После успешного пуша и в случае, если все переменные указаны верно проект запустится на сервере.

Далее в терминале, подключенном к боевому серверу вводим поочередно следующие команды:
```
sudo docker-compose exec web python manage.py makemigrations
```
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
```
sudo docker-compose exec web python manage.py createsuperuser
```
Проект зарущен, с помощью супрюзера можно подключаться

## Примеры запросов
### Регистрация пользователя
>Тип запроса 
```POST```
>Endpoint 
```api/v1/auth/signup/```

Запрос:
```
{
  "email": "user@example.com",
  "username": "string"
}
```
Ответ:
```
{
  "email": "string",
  "username": "string"
}
```
______________________________________
### Авторы
Даниил Алексеенко(https://github.com/cra1ger51),
Андрей Иванишин(https://github.com/AIvanishin),
Виталий Симоненко(https://github.com/SimoneVita)

### Лицензия
BSD 3-Clause License
