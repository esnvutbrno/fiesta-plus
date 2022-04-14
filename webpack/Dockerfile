# context is root of project, since we need
FROM node:17.8.0-slim

RUN apt-get update && apt-get install -y python python3 gcc g++ make build-essential

WORKDIR /usr/src/app

COPY ./webpack/package.json ./webpack/yarn.lock ./
RUN npm install yarn && yarn install

COPY ./webpack/ /usr/src/app/
COPY ./fiesta/ /usr/src/fiesta/

CMD ["yarn", "run"]
