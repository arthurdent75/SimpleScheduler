ARG BUILD_FROM
FROM ${BUILD_FROM}

# Update Packages
RUN apt-get update -y && apt upgrade -y

# Setup base
RUN apt-get install -y \
    coreutils \
    wget \
	curl \
	python3 \
	python3-dev \ 
	python3-pip
	
# Install python modules	
RUN pip3 install Flask requests paho-mqtt pytz psutil

# Copy root filesystem
COPY rootfs /

