FROM python:3.7.8-slim

ENV DEBIAN_FRONTEND=noninteractive
ARG VERSION=3.12-2

ADD . /

WORKDIR /

RUN apt update && \
    apt install --no-install-recommends -y git fio=${VERSION} && \
    git clone https://github.com/louwrentius/fio-plot && \
    rm -rf fio-plot/images && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r fio-plot/fio_plot/requirements.txt && \
    rm -rf /var/lib/apt/lists/* && \
    echo "plt.cla()" >> /fio-plot/fio_plot/fiolib/graph2d.py && \
    echo "plt.clf()" >> /fio-plot/fio_plot/fiolib/graph2d.py && \
    ln -s /fio-plot/benchmark_script/bench_fio /usr/local/bin/bench_fio && \
    ln -s /fio-plot/fio_plot/fio_plot /usr/local/bin/fio_plot
