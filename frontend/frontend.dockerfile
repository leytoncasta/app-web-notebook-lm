FROM node:18-alpine

WORKDIR /app

COPY package.json .

RUN npm install @emotion/react @emotion/styled @mui/material @mui/icons-material axios react-router-dom react-toastify
RUN npm install

RUN npm i -g serve

COPY . .

RUN npm run build

EXPOSE 3000

CMD [ "serve", "-s", "dist" ]