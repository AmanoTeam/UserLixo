FROM mcr.microsoft.com/devcontainers/python:3.11

RUN git config --global --add safe.directory /usr/src/userlixo

WORKDIR /backend
COPY ./requirements.lock /backend/
RUN sed '/-e/d' requirements.lock > requirements.txt
RUN pip install -r requirements.txt
