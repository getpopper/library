FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND=noninteractive
ARG VERSION=2.6

ENV PYTHONUNBUFFERED=on

RUN apt update && \
    apt install -y --no-install-recommends \
      git-core openssh-client && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir netaddr ansible==${VERSION}

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
