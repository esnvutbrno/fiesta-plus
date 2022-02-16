FROM node:17.4.0-slim

RUN apt-get update && apt-get install -y python python3 gcc g++ make build-essential

WORKDIR /usr/src/app

COPY package.json yarn.lock ./
RUN npm install yarn && yarn install

COPY ./*.config.js ./src/ /usr/src/app/

CMD ["yarn", "run"]
