![Actions Status](https://github.com/aleksandrtikhonov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# foodgram-project-react
 «Продуктовый помощник».
 
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 
### Деплой приложения
Склонировать репозиторий https://github.com/aleksandrtikhonov/foodgram-project-react.git

Создать github actions https://github.com/ваш_профиль/ваш_репозиторий/actions

Заменить содержимое .github/workflows/main.yaml на данные из foodgram_workflow.yaml(находится в корне проекта)

В https://github.com/ваш_профиль/ваш_репозиторий/settings/secrets/actions создать новые secrets

```shell
DB_ENGINE
DB_HOST
DB_NAME
DB_PORT
POSTGRES_PASSWORD
POSTGRES_USER
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
SSH_KEY
PASSPHRASE
TELEGRAM_TO
TELEGRAM_TOKEN
TELEGRAM_TOKEN
```

Скопировать на сервер директорию frontend

Скопировать на сервер файлы из директории infra

Запуск проекта:

```shell
docker-compose up -d
```

При внесении изменений в код на github, проект самостоятельно соберётся и задеплоится на сервер.
_______________________________________________________________

Ознакомиться с реализованными методами API:
```shell
http://localhost/api/docs/redoc.html
```
