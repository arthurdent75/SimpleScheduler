ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base/amd64:5.3.0
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends\
		apache2 \
		php7.4 \
		php7.4-curl \
		php7.4-intl \
		php7.4-mbstring \
		php7.4-json
		
		
COPY rootfs /