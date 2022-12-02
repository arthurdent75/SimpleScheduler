ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN pip3 install Flask requests paho-mqtt pytz slugify psutil

COPY rootfs /

WORKDIR /simplescheduler

CMD ["python3", "main.py" , "--host=0.0.0.0"]
