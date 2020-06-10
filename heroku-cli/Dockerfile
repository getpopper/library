FROM node:14.4-buster
ARG VERSION=7.42.1
ARG LIB_VERSION=4.2.1
WORKDIR usr/src/app
RUN npm install -g heroku@${VERSION}
RUN apt-get update -y
RUN apt-get install -y python3 python3-pip
RUN pip3 install heroku3==${LIB_VERSION}
CMD ["heroku"]
