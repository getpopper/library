#!/bin/bash
set -e

if [ -z "$ANSIBLE_SSH_KEY_DATA" ]; then
  echo "Expecting ANSIBLE_SSH_KEY_DATA"
  exit 1
fi

mkdir -p /root/.ssh
echo "$ANSIBLE_SSH_KEY_DATA" | base64 --decode > /root/.ssh/id_rsa
chmod 600 /root/.ssh
chmod 400 /root/.ssh/id_rsa

exec bash -c "ansible-playbook $*"
