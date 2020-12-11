FROM ubuntu:latest

ENV DEBIAN_FRONTEND="nointeractive"

RUN apt-get -qq update && \
  apt-get -qq install -y git python3 python3-pip curl ffmpeg locales tzdata
RUN apt update && apt install -y neofetch

RUN git clone https://github.com/AmanoTeam/UserLixo /usr/src/app/Userlixo
WORKDIR /usr/src/app/Userlixo

RUN pip3 install -U pip setuptools wheel
RUN pip3 install -Ur requirements-heroku.txt

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

CMD ["python3", "-m", "userlixo"]
