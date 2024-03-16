FROM node:21-bookworm-slim as build-stage

WORKDIR /app

ARG PUBLIC_DOC_VERSION
ARG PUBLIC_DOC_BUILD_TIMESTAMP

COPY . .
RUN npm install
RUN npm run check
RUN npm run build

FROM nginx:1.25-bookworm as production

RUN apt-get update && apt-get install nodejs npm -y
RUN npm install pm2 -g

COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY --from=build-stage /app/build .
COPY --from=build-stage /app/package.json .

ENV PORT=8001
EXPOSE ${PORT}

CMD ["/bin/sh",  "-c",  "pm2 start 'node index.js' && exec nginx -g 'daemon off;'"]
