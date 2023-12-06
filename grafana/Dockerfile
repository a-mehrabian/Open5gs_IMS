FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y wget && \
    wget -q https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz && \
    tar xvfz grafana-10.2.2.linux-amd64.tar.gz

WORKDIR grafana-v10.2.2

CMD /mnt/grafana/grafana_init.sh