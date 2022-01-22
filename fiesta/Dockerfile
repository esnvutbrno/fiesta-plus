# pull official base image
FROM python:3.9.7-alpine


# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# same for postgres container
ENV TZ Europe/Prague

# configure users, dirs, install psycopg, install runtime deps
RUN addgroup -S 1000 \
    && adduser -s /bin/sh -D -S -G 1000 1000 \
    && apk update \
    #   build deps
    && apk add --virtual build-deps gcc python3-dev musl-dev gettext-dev libffi-dev \
    && pip install poetry \
    #  runtime deps
    && apk add postgresql-dev gettext tzdata bash \
    # && pipenv install psycopg2-binary --skip-lock --dev \
    && apk del build-deps \
    && mkdir -p /usr/src/static /usr/src/media /usr/src/app \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install python deps
COPY pyproject.toml poetry.lock /usr/src/app/
RUN apk add --virtual python-deps build-base \
    && poetry config virtualenvs.create false \
    && poetry install \
    && apk del python-deps

# copy project
COPY ./fiesta/ /usr/src/app/

RUN chown 1000:1000 -R /usr/src
USER 1000
