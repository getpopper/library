FROM node:14.4-buster

ARG VERSION=1.2.2

WORKDIR usr/src/app
RUN apt-get -y update && \
    apt-get install -y ca-certificates && \
    npm -g config set user root && \
    npm install -g hasura-cli@${VERSION} && \
    rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["hasura"]
