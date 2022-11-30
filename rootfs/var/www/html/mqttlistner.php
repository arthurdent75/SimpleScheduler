<?php
	
echo '[' . date('r') . "] Starting MQTT Listner...\n";
	
include_once("lib.php");

if (!$options->MQTT->enabled) die("MQTT disabled");


$client_id = 'simplescheduler-'.uniqid() ; 
$mqtt = new phpMQTT($options->MQTT->server, $options->MQTT->port, $client_id);

$lwt=array(
	'topic'=>'homeassistant/switch/simplescheduler/availability',
	'content'=>'offline',
	'retain'=>1,
	'qos'=>0
);

if ($mqtt->connect(true, $lwt ,  $options->MQTT->username, $options->MQTT->password)) {
	
	sleep(1);
	
	$mqtt->publish("homeassistant/switch/simplescheduler/availability", "online", 0, true);
	
	refresh_switches($mqtt,false);
	
	$topics["homeassistant/switch/simplescheduler/#"] = array('qos' => 0, 'function' => 'procMsg');
	$mqtt->subscribe($topics);

	while($mqtt->proc()) {
		if (date("s")=="00") refresh_switches($mqtt);
	}	
	
	$mqtt->close();
	
} else {
	echo '[' . date('r') . "] Unable to connecto to MQTT broker! \n";
}


function refresh_switches($mqtt_obj, bool $clear = false ) {

	$sched = load_data();
	$config_topic_template="homeassistant/switch/simplescheduler/###/config";
	$payload_template='{"name": "simplescheduler_###_@@@" , "unique_id": "simplescheduler_###_@@@", "icon":"mdi:calendar-clock" , "command_topic": "homeassistant/switch/simplescheduler/###/set", "state_topic": "homeassistant/switch/simplescheduler/###/state","availability_topic": "homeassistant/switch/simplescheduler/availability","payload_available":"online","payload_not_available":"offline"}';

	if ($clear) {
		foreach ($sched as $s) {
			$topic=str_replace('###',$s->id,$config_topic_template);
			$mqtt_obj->publish($topic, null, 0, true);
		}
		sleep(2);
	}
	
	foreach ($sched as $s) {
		$topic=str_replace('###',$s->id,$config_topic_template);
		$payload=str_replace('###',$s->id,$payload_template);
		$payload=str_replace('@@@',slugify($s->name),$payload);
	    $mqtt_obj->publish($topic, $payload, 0, false);
		mqtt_publish_state($s->id,$s->enabled , false);
	}
	sleep(1);
}

function procMsg($topic, $msg){
		$pieces = explode('/', $topic);
		$v = ($msg=="ON") ? 1 : 0 ;
		if (strtolower($pieces[4])=="set") {
			$id=$pieces[3];
			file_get_contents( "http://localhost?action=setstate&id=$id&v=$v" );
			file_get_contents( 'http://localhost?action=setdirt' );
			echo '[' . date('r') . "] RCV: {$topic} --> $msg \n";
			mqtt_publish_state($pieces[3],$v,true);
		}
}