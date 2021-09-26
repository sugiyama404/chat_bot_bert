FROM python:3.8.8-buster
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

ENV PYTHONPYCACHEPREFIX=/root/pycache

RUN apt-get install -y vim less sqlite3
RUN pip install --upgrade pip --user
RUN pip install --upgrade setuptools --user

RUN wget --quiet http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O ta-lib-0.4.0-src.tar.gz && \
    tar xvf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    pip install TA-Lib --user && \
    rm -R ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /root/opt

COPY ./opt .
