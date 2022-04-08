FROM python:3.11.0a7-alpine as builder

RUN apk add --no-cache --virtual build-deps \
    build-base gcc python3-dev musl-dev gettext-dev libffi-dev g++ \
    postgresql-dev mariadb-dev libxml2-dev libxslt-dev \
    musl-dev rust cargo patchelf git jpeg-dev zlib-dev

COPY pyproject.toml poetry.lock ./

RUN python -m pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install && \
    apk del build-deps


# pull official base image
FROM python:3.11.0a7-alpine

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# same for postgres container
ENV TZ Europe/Prague

COPY pyproject.toml poetry.lock /usr/src/app/

# configure users, dirs, install psycopg, install runtime deps
RUN addgroup -S 1000 \
    && adduser -s /bin/sh -D -S -G 1000 1000 \
    && apk update \
    # runtime deps
    && apk add gettext tzdata bash graphviz graphviz-dev ttf-freefont postgresql-dev mariadb-dev libmagic \
    # && pipenv install psycopg2-binary --skip-lock --dev \
    && mkdir -p /usr/src/static /usr/src/media /usr/src/app \
    && chown 1000:1000 -R /usr/src \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# copy project
COPY ./fiesta/ /usr/src/app/

RUN chown 1000:1000 -R /usr/src && chmod a+wrx -R /usr/src

ENTRYPOINT ["./run.sh"]
