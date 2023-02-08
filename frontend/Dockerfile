# Stage 0: build the frontend.
FROM node:19-bullseye-slim as development-stage

RUN apt-get update && apt-get install -y \
    python3  \
    make  \
    g++

WORKDIR /app

COPY . .
RUN npm install

# Enforce typescript strict type checking and if no errors, proceed.
RUN npm run check

# 'npm run build' will run 'vite build' which will create the
# ./dist directory containing the built project. Note too that 'npm
# run build' puts the frontend build system (vite) into production mode
# which means that the values in .env.production will have priority
# over same in .env
RUN npm run build

# Stage 1: Let nginx serve the built front-end in production.
FROM nginx:1.23

RUN apt-get update && apt-get install -y \
    moreutils # For sponge

COPY --from=development-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY --from=development-stage /app/dist/ /usr/share/nginx/html
COPY --from=development-stage /app/envvars.js /usr/share/nginx/html/assets/
EXPOSE 80

# When the container starts, replace the envvars.js with values from environment variables
CMD ["/bin/sh",  "-c",  "envsubst < /usr/share/nginx/html/assets/envvars.js | sponge /usr/share/nginx/html/assets/envvars.js && exec nginx -g 'daemon off;'"]
