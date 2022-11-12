FROM ubuntu:latest

# update sources and install git
RUN apt-get update -y && apt-get install -y git python3-pip

# git configuration
RUN git config --global user.name "YOUR NAME HERE" \
    && git config --global user.email "YOUR EMAIL HERE"

# clone mksec
RUN git clone --depth=1 https://github.com/generatorexit/mksec.git

# change working directory
WORKDIR /mksec

# install requirements
RUN pip3 install -r requirements.txt

# install mksec
RUN python3 setup.py

ENTRYPOINT [ "./mksec" ]