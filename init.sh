
FOLDER=/share/simplescheduler

mkdir -p $FOLDER

cp /data/options.json $FOLDER/options.dat
if [ -f $FOLDER/options.json ]; then
	rm $FOLDER/options.json 
fi

chmod -R 777 $FOLDER
chown -R www-data:www-data $FOLDER

php /var/www/html/scheduler.php | tee -a $FOLDER/simplescheduler.log &
sudo -E -u www-data php /var/www/html/mqttlistner.php | tee -a $FOLDER/simplescheduler.log &

apache2-foreground > /dev/null 2>&1