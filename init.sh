
FOLDER=/share/simplescheduler

mkdir -p $FOLDER

cp /data/options.json $FOLDER/options.dat
rm $FOLDER/options.json 

chmod -R 777 $FOLDER

php /var/www/html/scheduler.php >> $FOLDER/scheduler.log &

apache2-foreground