FROM python:3.10-bullseye

RUN git config --global --add safe.directory /usr/src/userlixo

RUN apt-get update && apt-get install -y \
    git python3-dev python3-pip python3-setuptools

COPY .docker .docker

ENV IS_DOCKER=1

ENTRYPOINT ["/bin/bash", ".docker/entrypoint.sh"]
