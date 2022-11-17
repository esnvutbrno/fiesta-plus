FROM python:alpine as builder

ARG POETRY_EXPORT_ARGS

# build deps
RUN apk add --no-cache \
    build-base gcc python3-dev musl-dev gettext-dev libffi-dev g++ \
    postgresql-dev mariadb-dev libxml2-dev libxslt-dev \
    musl-dev rust cargo patchelf git jpeg-dev zlib-dev

# final venv
RUN python -m venv /venv
# poetry to export & install
RUN python -m pip install poetry
# to speed up install process (whl are much smaller and quicker)
RUN /venv/bin/pip install wheel
COPY pyproject.toml poetry.lock ./
# no hashes since we use deps from .git urls
RUN poetry export --without-hashes ${POETRY_EXPORT_ARGS} -o /tmp/requirements.txt
RUN /venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# pull official base image
FROM python:alpine

COPY --from=builder /venv /venv

# set work directory
WORKDIR /usr/src/app

ENV PATH="/venv/bin:${PATH}"
ENV VIRTUAL_ENV="/venv"
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
