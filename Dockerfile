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

ARG SENTRY_RELEASE_ENVIRONMENT
ENV SENTRY_RELEASE_ENVIRONMENT=${SENTRY_RELEASE_ENVIRONMENT}

RUN \
  --mount=type=secret,id=SENTRY_ORG \
  --mount=type=secret,id=SENTRY_PROJECT \
  --mount=type=secret,id=SENTRY_WEBPACK_AUTH_TOKEN \
  --mount=type=secret,id=SENTRY_RELEASE_NAME \
  --mount=type=secret,id=SENTRY_RELEASE_ENVIRONMENT \
  export SENTRY_ORG=$(cat /run/secrets/SENTRY_ORG) \
  export SENTRY_PROJECT=$(cat /run/secrets/SENTRY_PROJECT) \
  export SENTRY_WEBPACK_AUTH_TOKEN=$(cat /run/secrets/SENTRY_WEBPACK_AUTH_TOKEN) \
  export SENTRY_RELEASE_NAME=$(cat /run/secrets/SENTRY_RELEASE_NAME) \
  export SENTRY_RELEASE_ENVIRONMENT=$(cat /run/secrets/SENTRY_RELEASE_ENVIRONMENT) \
  && yarn build

#
# django web app image
#

# venv builder
FROM python:3.11.3-alpine3.17 as web-venv-builder

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
FROM python:3.11.3-alpine3.17 as web-base

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

ARG DJANGO_RELASE_NAME
ENV DJANGO_RELASE_NAME=${DJANGO_RELASE_NAME}

# need production configuration, but not all values are ready in env
RUN bash -c "DJANGO_SECRET_KEY=\$RANDOM DJANGO_CONFIGURATION=LocalProduction python manage.py collectstatic --no-input"

# given by webpack compiled results
COPY --from=webpack-stable /usr/src/build/webpack-stats.json ${DJANGO_BUILD_DIR}

# TODO: check opts https://www.uvicorn.org/#command-line-options
CMD ["python -m gunicorn -b [::]:8000 fiesta.wsgi:application"]

#
# proxy image
#
FROM nginx:1.25.0-alpine as proxy-base

RUN rm /etc/nginx/conf.d/default.conf

# https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration-new-in-119
COPY ./nginx/nginx.conf.template /etc/nginx/templates/

FROM proxy-base as proxy-stable

# prepared by webpack and web builds during CD
COPY --from=webpack-stable /usr/src/build/ /var/build/
COPY --from=web-stable /usr/src/static/ /var/static/

ARG STATIC_LOCATION_PATTERN="^/static/(.*)$$"
ENV STATIC_LOCATION_PATTERN=${STATIC_LOCATION_PATTERN}

ARG PROXY_HOSTNAME_TARGET="127.0.0.1"
ENV PROXY_HOSTNAME_TARGET=${PROXY_HOSTNAME_TARGET}

CMD ["nginx", "-g", "daemon off;"]
