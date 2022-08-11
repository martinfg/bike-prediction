###############################################################################
# build stage
###############################################################################
FROM node:18-alpine AS build

WORKDIR /usr/src/app

COPY --chown=node:node package*.json ./
COPY --chown=node:node . .

RUN npm install

ENV NODE_ENV=production
ENV VITE_BACKEND_URL="https://t8.se4ai.sws.informatik.uni-leipzig.de/api/"

RUN npm run build

USER node



###############################################################################
# production stage
###############################################################################
FROM nginx:stable-alpine AS production

WORKDIR /usr/share/nginx/html

COPY --chown=nginx:nginx --from=build /usr/src/app/dist .

COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
