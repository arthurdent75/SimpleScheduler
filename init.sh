
FOLDER=/share/simplescheduler

mkdir -p $FOLDER

chmod -R 777 $FOLDER

php /var/www/html/scheduler.php >> $FOLDER/scheduler.log &

apache2-foreground