FROM debian:bullseye-20200514-slim
RUN apt update && \
    apt install -y csvtool && \
    rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["csvtool"]
