#!/bin/bash
set -e

if [[ $# == 0 ]]; then
  echo "Expecting one or more arguments to entrypoint"
  exit 1
fi

function check_variable {
  if [ -z "${!1}" ]; then
    echo "Expecting variable $1"
    exit 1
  fi
}

check_variable GENI_FRAMEWORK
check_variable GENI_USERNAME
check_variable GENI_PROJECT
check_variable GENI_PUBKEY_DATA
check_variable GENI_CERT_DATA
check_variable GENI_KEY_PASSPHRASE

echo "$GENI_CERT_DATA" | base64 --decode > /tmp/geni.cert
echo "$GENI_PUBKEY_DATA" | base64 --decode > /tmp/pub.key

cat > /geni-context.json <<EOL
{"user-name": "$GENI_USERNAME",
 "cert-path": "/tmp/geni.cert",
 "key-path": "/tmp/geni.cert",
 "user-pubkeypath": "/tmp/pub.key",
 "project": "$GENI_PROJECT",
 "framework": "$GENI_FRAMEWORK",
 "user-urn": "urn:publicid:IDN+emulab.net+user+$GENI_USERNAME"
}
EOL

exec python $@
