
FOLDER=/share/simplescheduler

mkdir -p $FOLDER

cp /data/options.json $FOLDER/options.dat
if [ -f $FOLDER/options.json ]; then
	rm $FOLDER/options.json 
fi

chmod -R 777 $FOLDER

php /var/www/html/scheduler.php >> $FOLDER/scheduler.log &

apache2-foreground