# context is root of project, since we need access to Django app source files
FROM node:18-slim

RUN apt-get update && apt-get install -y python python3 gcc g++ make build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./webpack/package.json ./webpack/yarn.lock ./
RUN npm install yarn && yarn install

COPY ./webpack/ /usr/src/app/
COPY ./fiesta/ /usr/src/fiesta/

CMD ["yarn", "run"]
