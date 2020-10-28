FROM php:7.3-apache 

COPY 000-default.conf /etc/apache2/sites-enabled
COPY /web /var/www/html
RUN chown -R  www-data:www-data /var/www/html
RUN chmod -R  775 /var/www/html

COPY init.sh /home
RUN chmod a+x /home/init.sh

EXPOSE 7777

CMD /home/init.sh

