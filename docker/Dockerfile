FROM ubuntu:latest
LABEL author="Kieran White" email="whiteks@aston.ac.uk"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	python3-pip \
	python3-dev \
	build-essential\
	vim \
	libssl-dev \
	libxml2 \
	libxml2-dev \
	unixodbc-dev \
	libgl1-mesa-glx \
	python3-tk \
	ghostscript \
	&& apt-get clean

# install python requirements
RUN apt-get install -y python3-setuptools
RUN pip3 install --upgrade pip
COPY document_parser/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

WORKDIR /app
COPY document_parser /app

EXPOSE 5000

ENTRYPOINT ["/usr/bin/python3"]
CMD ["app.py"]
