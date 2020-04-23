FROM python:3.7.7-slim-stretch

ENV DEBIAN_FRONTEND=noninteractive
ARG VERSION=stable-5.0

ENV PYTHONUNBUFFERED=on

RUN apt update && \
    apt install -y --no-install-recommends \
      git-core openssh-client && \
    rm -rf /var/lib/apt/lists/* && \
# clone given version \
    git clone --depth=1 --branch=${VERSION} https://github.com/ceph/ceph-ansible && \
# install requirements (this installs ansible as well) \
    pip install --no-cache-dir -r ceph-ansible/requirements.txt && \
# move roles, library and plugins to default paths \
    mkdir -p /etc/ansible /share/ansible && \
    mv ceph-ansible/roles /etc/ansible/ && \
    mv ceph-ansible/library /usr/share/ansible/ && \
    mv ceph-ansible/plugins /usr/share/ansible/ && \
    rm -r ceph-ansible

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
