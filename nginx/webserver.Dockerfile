# syntax = edrevo/dockerfile-plus

FROM nginx:1.21.5-alpine

RUN rm /etc/nginx/conf.d/default.conf

INCLUDE+ Dockerfile.common

# https://github.com/docker-library/docs/tree/master/nginx#using-environment-variables-in-nginx-configuration-new-in-119
COPY ./nginx.conf.template /etc/nginx/templates/
