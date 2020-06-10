FROM node:current-slim
ARG VERSION=1.2.2
WORKDIR usr/src/app
ENV NPM_CONFIG_PREFIX /home/node/.npm-global
ENV PATH $PATH:/home/node/.npm-global/bin
USER node
RUN npm install -g hasura-cli@${VERSION}
CMD ["hasura"]
