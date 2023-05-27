FROM nginx:1.25.0-alpine as base

RUN rm /etc/nginx/conf.d/default.conf

# https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration-new-in-119
COPY ./nginx/nginx.conf.template /etc/nginx/templates/

FROM base as stable

# propared by webpack and web builds during CD
COPY webpack-build/ /var/build/
COPY web-static/ /var/static/

ARG STATIC_LOCATION_PATTERN="^/static/(.*)$$"
ENV STATIC_LOCATION_PATTERN=${STATIC_LOCATION_PATTERN}

ARG PROXY_HOSTNAME_TARGET="127.0.0.1"
ENV PROXY_HOSTNAME_TARGET=${PROXY_HOSTNAME_TARGET}

CMD ["nginx", "-g", "daemon off;"]
