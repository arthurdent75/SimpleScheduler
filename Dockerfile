FROM ghcr.io/hassio-addons/base-python:16.1.0

RUN pip3 install Flask requests pytz psutil paho-mqtt 

COPY rootfs /
