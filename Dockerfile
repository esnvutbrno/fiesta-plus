# expected to be set during production build
ARG DJANGO_RELEASE_NAME
ARG SENTRY_RELEASE_NAME
ARG SENTRY_RELEASE_ENVIRONMENT

ARG PYTHON_IMAGE=python:3.12.6-alpine3.20

#
# wiki renderer image
#
FROM ruby:3.0 as wiki-base

RUN apt-get update && \
    # pip to install docutils, cmake to build github-linguist
    apt-get install -y python3-pip cmake && \
    python3 -m pip install docutils && \
    apt-get remove -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY ./wiki/Gemfile ./wiki/Gemfile.lock ./
RUN bundle install

RUN apt-get remove -y cmake && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./wiki/ .

ENTRYPOINT [ "./fetcher.rb" ]

FROM wiki-base as wiki-stable

ENV WIKI_GIT_URL=https://github.com/esnvutbrno/fiesta-plus.wiki.git
ENV WIKI_STATIC_ASSETS_URL=/static/gh/

ENV WIKI_DB_PATH=/usr/src/wiki/db
ENV WIKI_DB_NAME=${WIKI_DB_PATH}/wiki.sqlite3
ENV WIKI_STATIC_PATH=/usr/src/wiki/static
ENV WIKI_STATIC_URL=/static/wiki/

RUN mkdir -p $WIKI_STATIC_PATH && mkdir -p $WIKI_DB_PATH && ./fetcher.rb

#
# webpack image
#
FROM node:18.15.0-slim as webpack-base

RUN apt-get update && apt-get install -y python python3 gcc g++ make build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./webpack/package.json ./webpack/yarn.lock ./
RUN --mount=type=cache,target=/root/.yarn YARN_CACHE_FOLDER=/root/.yarn npm install yarn && yarn install

COPY ./webpack/ /usr/src/app/
COPY ./fiesta/ /usr/src/fiesta/

CMD ["yarn", "run"]

# stable image
FROM webpack-base as webpack-stable

ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}

ARG BUILD_DIR=/usr/src/build
ENV BUILD_DIR=${BUILD_DIR}

ARG PUBLIC_PATH=/static/
ENV PUBLIC_PATH=${PUBLIC_PATH}

ARG TAILWIND_CONTENT_PATH="/usr/src/fiesta/**/templates/**/*.html:/usr/src/fiesta/**/*.py"
ENV TAILWIND_CONTENT_PATH=${TAILWIND_CONTENT_PATH}

ARG SENTRY_RELEASE_NAME
ENV SENTRY_RELEASE_NAME=${SENTRY_RELEASE_NAME}

ARG SENTRY_RELEASE_ENVIRONMENT
ENV SENTRY_RELEASE_ENVIRONMENT=${SENTRY_RELEASE_ENVIRONMENT}

RUN \
  --mount=type=secret,id=SENTRY_ORG \
  --mount=type=secret,id=SENTRY_PROJECT \
  --mount=type=secret,id=SENTRY_WEBPACK_AUTH_TOKEN \
  export SENTRY_ORG=$(cat /run/secrets/SENTRY_ORG) \
  export SENTRY_PROJECT=$(cat /run/secrets/SENTRY_PROJECT) \
  export SENTRY_WEBPACK_AUTH_TOKEN=$(cat /run/secrets/SENTRY_WEBPACK_AUTH_TOKEN) \
  && yarn build

#
# django web app image
#

# venv builder
FROM ${PYTHON_IMAGE} as web-venv-builder

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
RUN --mount=type=cache,target=/root/.cache/pip /venv/bin/pip install -r /tmp/requirements.txt

# base runtime image
FROM ${PYTHON_IMAGE} as web-base

COPY --from=web-venv-builder /venv /venv

# set work directory
WORKDIR /usr/src/app

ENV PATH="/venv/bin:${PATH}"
ENV VIRTUAL_ENV="/venv"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "fiesta.settings"
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

# stable image runtime
FROM web-base as web-stable

# stubs to get compatibility with fs storage
ARG DJANGO_STATIC_ROOT=/usr/src/static
ENV DJANGO_STATIC_ROOT=${DJANGO_STATIC_ROOT}
ARG DJANGO_MEDIA_ROOT=/usr/src/media
ENV DJANGO_MEDIA_ROOT=${DJANGO_MEDIA_ROOT}

# TODO: maybe better name?
ARG DJANGO_BUILD_DIR=/usr/src/build/
ENV DJANGO_BUILD_DIR=${DJANGO_BUILD_DIR}

ARG DJANGO_RELEASE_NAME
ENV DJANGO_RELEASE_NAME=${DJANGO_RELEASE_NAME}

# need production configuration, but not all values are ready in env
RUN bash -c "DJANGO_SECRET_KEY=\$RANDOM DJANGO_CONFIGURATION=LocalProduction python manage.py collectstatic --no-input --verbosity 3"

# given by webpack compiled results
COPY --from=webpack-stable /usr/src/build/webpack-stats.json ${DJANGO_BUILD_DIR}

COPY --from=wiki-stable /usr/src/wiki/db/wiki.sqlite3 /usr/src/wiki/db/wiki.sqlite3

# TODO: check opts https://www.uvicorn.org/#command-line-options
CMD ["python -m gunicorn -b [::]:8000 fiesta.wsgi:application"]

#
# proxy image
#
FROM nginx:1.26.0-alpine as proxy-base

RUN rm /etc/nginx/conf.d/default.conf

# https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration-new-in-119
COPY ./nginx/nginx.conf.template /etc/nginx/templates/

FROM proxy-base as proxy-stable

# prepared by webpack and web builds during CD
COPY --from=webpack-stable /usr/src/build/ /var/build/
COPY --from=web-stable /usr/src/static/ /var/static/
COPY --from=wiki-stable /usr/src/wiki/static /var/static/wiki/

ARG STATIC_LOCATION_PATTERN="^/static/(.*)$$"
ENV STATIC_LOCATION_PATTERN=${STATIC_LOCATION_PATTERN}

ARG PROXY_HOSTNAME_TARGET="127.0.0.1"
ENV PROXY_HOSTNAME_TARGET=${PROXY_HOSTNAME_TARGET}

CMD ["nginx", "-g", "daemon off;"]
