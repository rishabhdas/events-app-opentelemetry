FROM node:18.12.1

WORKDIR /app

ADD index.js /app
ADD tracing.js /app
ADD package.json /app

RUN npm install
EXPOSE 3000

CMD ["npm", "start"]