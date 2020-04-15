FROM python:2.7-slim-jessie

RUN pip install --no-cache-dir geni-lib==0.9.9.2

ENV PYTHONUNBUFFERED=on

COPY scripts/* /usr/bin/
COPY util.py /usr/local/lib/python2.7/site-packages/geni/

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
