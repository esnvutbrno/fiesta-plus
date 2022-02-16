FROM nginxproxy/nginx-proxy:alpine
RUN { \
  echo 'server_tokens off;'; \
  echo 'client_max_body_size 100m;'; \
} > /etc/nginx/conf.d/proxy.conf
