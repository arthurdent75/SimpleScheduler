#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: SimpleScheduler
# Configures requirements
# ==============================================================================

rm -f /var/www/html/index.html

FOLDER=/share/simplescheduler

mkdir -p $FOLDER

cp /data/options.json $FOLDER/options.dat

# In older version the option file was named option.json
# If such file exists, delete it
if [ -f $FOLDER/options.json ]; then
	rm $FOLDER/options.json 
fi

touch $FOLDER/dirt.dat

chmod -R 777 $FOLDER
chown -R www-data:www-data $FOLDER


bashio::log.info  'Starting Scheduler'
php /var/www/html/scheduler.php | tee -a $FOLDER/simplescheduler.log &

if bashio::config.true 'MQTT.enabled'; then
	bashio::log.info  'Starting MQTT Listener'
	php /var/www/html/mqttlistner.php | tee -a $FOLDER/simplescheduler.log &
fi
	



