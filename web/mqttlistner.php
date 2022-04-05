<?php
	
include_once("lib.php");

if (!$options->MQTT->enabled) die();

echo "Starting MQTT Listner...\n";
	
$client_id = 'simplescheduler-'.uniqid() ; 
$mqtt = new phpMQTT($options->MQTT->server, $options->MQTT->port, $client_id);


if ($mqtt->connect(true, NULL,  $options->MQTT->username, $options->MQTT->password)) {
	
	refresh_switches($mqtt,true);
	
	$topics["homeassistant/switch/simplescheduler/#"] = array('qos' => 0, 'function' => 'procMsg');
	$mqtt->subscribe($topics);

	while($mqtt->proc()) {
		if (date("s")=="00") refresh_switches($mqtt);
	}	
	
	$mqtt->close();
} 


function refresh_switches($mqtt_obj, bool $clear = false ) {

	// echo "Refreshing switches \n";
	$sched = load_data();

	$config_topic_template="homeassistant/switch/simplescheduler/###/config";
	$payload_template='{"name": "simplescheduler_###_@@@" , "unique_id": "simplescheduler_###_@@@", "icon":"mdi:calendar-clock" , "command_topic": "homeassistant/switch/simplescheduler/###/set", "state_topic": "homeassistant/switch/simplescheduler/###/state"}';

	foreach ($sched as $s) {
		$topic=str_replace('###',$s->id,$config_topic_template);
		$payload=str_replace('###',$s->id,$payload_template);
		$payload=str_replace('@@@',slugify($s->name),$payload);
		if ($clear) $mqtt_obj->publish($topic, null, 0, true);
	    $mqtt_obj->publish($topic, $payload, 0, false);
		mqtt_publish_state($s->id,$s->enabled , false);
	}
	sleep(1);
}

function procMsg($topic, $msg){
		$pieces = explode('/', $topic);
		$v = ($msg=="ON") ? true : false ;
		if (strtolower($pieces[4])=="set") {
			$id=$pieces[3];
			change_state_in_json_file($id,$v);	
			set_dirt();
			echo '[' . date('r') . "] RCV: {$topic} --> $msg \n";
			mqtt_publish_state($pieces[3],$v,true);
		}
}