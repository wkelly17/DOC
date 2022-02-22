# Stage 0, "development-stage", based on Node.js, to build the
# frontend and run it in 'development' mode.
FROM node:17.5.0-bullseye-slim as development-stage

RUN apt-get update && apt-get install -y \
    python3  \
    make  \
    g++

WORKDIR /app

COPY *.json /app/

RUN npm install

COPY ./ /app/

# Comment out the next line to disable tests
# RUN npm run test:unit

# Enforce typescript strict type checking and if no errors, proceed.
RUN npm run check

# 'npm run build' will run 'vite build' which will create the
# ./dist directory containing the built project.
RUN npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.21.6
COPY --from=development-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY --from=development-stage /app/dist/ /usr/share/nginx/html
EXPOSE 80
