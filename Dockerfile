FROM python:3.7
FROM php:7.3-apache 

COPY 000-default.conf /etc/apache2/sites-enabled
COPY /web /var/www/html

COPY init.sh /home
RUN chmod a+x /home/init.sh

EXPOSE 7777

CMD /home/init.sh

