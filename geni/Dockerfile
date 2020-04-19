FROM python:2.7-slim-jessie

ARG VERSION=0.9.9.2

RUN pip install --no-cache-dir geni-lib==${VERSION}

# - disable python buffering
# - give preference to our build-context script
ENV PYTHONUNBUFFERED=on \
    PATH=/usr/bin/:$PATH

COPY entrypoint.sh /
COPY util.py /usr/local/lib/python2.7/site-packages/geni/

ENTRYPOINT ["/entrypoint.sh"]
