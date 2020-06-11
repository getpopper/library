FROM node:14.4-buster

ARG VERSION=7.42.1
ARG PYTHON_LIB_VERSION=4.2.1

WORKDIR usr/src/app
RUN npm install -g heroku@${VERSION} && \
    apt-get update -y && \
    apt-get install -y python3 python3-pip && \
    pip3 --no-cache-dir install heroku3==${PYTHON_LIB_VERSION} && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["heroku"]
