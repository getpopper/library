#!/bin/bash
set -e

if [ -z "$GENI_BUNDLE_DATA" ]; then
  echo "Expecting GENI_BUNDLE_DATA variable"
  exit 1
fi

echo "$GENI_BUNDLE_DATA" | base64 --decode > /tmp/geni.bundle

context-from-bundle --bundle /tmp/geni.bundle
