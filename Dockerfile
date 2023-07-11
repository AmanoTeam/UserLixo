FROM mcr.microsoft.com/devcontainers/python:3.11

RUN sudo apt-get update && \
  sudo apt-get install -y python3-poetry

RUN git config --global --add safe.directory /usr/src/userlixo

ENV POETRY_VIRTUALENVS_IN_PROJECT true