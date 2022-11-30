ARG BUILD_FROM
FROM $BUILD_FROM

RUN pip3 install Flask requests paho-mqtt pytz slugify psutil

COPY rootfs /