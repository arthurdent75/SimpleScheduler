<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);

include_once("conf.php");

date_default_timezone_set(get_ha_timezone());

$logfile="/share/simplescheduler/scheduler.log";
$sun_file_age = 3600 * 6;
$options_json = @file_get_contents($options_json_file);
if (!$options_json) $options_json='{"translations":{"text_monday":"Monday","text_tuesday":"Tuesday","text_wednesday":"Wednesday","text_thursday":"Thursday","text_friday":"Friday","text_saturday":"Saturday","text_sunday":"Sunday","text_ON":"Turn ON","text_OFF":"Turn OFF","text_save":"Save","text_enabled":"Enabled","text_device":"Device"},"components":{"light":true,"scene":true,"switch":true,"script":true,"camera":true,"climate":true,"automation":true,"input_boolean":true,"media_player":true},"debug":false}';
$options = json_decode($options_json);
$translations = $options->translations;
$components = (array) $options->components;
$weekdays = Array("",
	$translations->text_monday,
	$translations->text_tuesday,
	$translations->text_wednesday,
	$translations->text_thursday,
	$translations->text_friday,
	$translations->text_saturday,
	$translations->text_sunday 
	);		

if ($options->debug) {
		error_reporting(E_ALL);
    } else {
		error_reporting(0);
	}

	
$switch_friendly_name=array();

function get_switch_list() {
	global $switch_friendly_name;
	global $SUPERVISOR_TOKEN;
	global $HASSIO_URL;
	global $components;
	
	
	$full_switch_list = array();
	$curlSES=curl_init(); 
	curl_setopt($curlSES,CURLOPT_URL,"$HASSIO_URL/states");
	curl_setopt($curlSES,CURLOPT_RETURNTRANSFER,true);
	curl_setopt($curlSES, CURLOPT_HTTPHEADER, array(
		'content-type: application/json',
		"Authorization: Bearer $SUPERVISOR_TOKEN"
	));
	
	$result = json_decode( curl_exec($curlSES) );
	curl_close($curlSES);

	if (is_array($result)) save_sunset_sunrise($result);
	
	foreach ($components as $c=>$cstate) :
		if ($cstate) :
			$switch_list = array();
			foreach ($result as $item) :
				$eid = $item->entity_id;
				if ( substr( $eid, 0, strlen($c) ) === $c ) :
					$switch = new stdClass();
					$switch->entity_id = $eid;
					$switch->friendly_name =  (isset($item->attributes->friendly_name)) ? $item->attributes->friendly_name : "" ;
					$switch->state = $item->state;
					$switch_list[] = $switch;
					$switch_friendly_name[$eid] = (isset($item->attributes->friendly_name)) ? $item->attributes->friendly_name : "" ;
					unset($switch);
				endif;
			endforeach;
			usort($switch_list, function($a, $b) { return ($a->friendly_name=="") ? 1 : strcasecmp($a->friendly_name, $b->friendly_name)  ; } );
			$full_switch_list = array_merge($full_switch_list,$switch_list);
		endif;
	endforeach;
	
	return $full_switch_list;
}	


function call_HA (Array $eid_list, string $action ) {
	global $SUPERVISOR_TOKEN;
	global $HASSIO_URL;
	$result ="";
	
	foreach ($eid_list as $eid):
			$domain = explode(".",$eid);
			$command_url = $HASSIO_URL . "/services/" . $domain[0] . "/turn_" . $action;
			
			$postdata = "{\"entity_id\":\"$eid\"}" ;
			
			$curlSES=curl_init(); 
			curl_setopt($curlSES,CURLOPT_RETURNTRANSFER, 1);
			curl_setopt($curlSES,CURLOPT_URL,"$command_url");
			curl_setopt($curlSES,CURLOPT_POST, 1);
			// curl_setopt($curlSES,CURLOPT_VERBOSE, 1);
			curl_setopt($curlSES,CURLOPT_SSL_VERIFYPEER, 0);
			curl_setopt($curlSES,CURLOPT_POSTFIELDS, $postdata);
			curl_setopt($curlSES,CURLOPT_HTTPHEADER, array(
				'content-type: application/json',
				"Authorization: Bearer $SUPERVISOR_TOKEN"
			));
			
			//$result += curl_exec($curlSES);
			$foo = curl_exec($curlSES);
			curl_close($curlSES);	
			$ts = date("Y-m-d H:i");
			echo "\n$ts --> Turning $action $eid";
	endforeach;
	
	return $result;
}

function get_ha_timezone() {
	global $SUPERVISOR_TOKEN;
	global $HASSIO_URL;
	
	$curlSES=curl_init(); 
	curl_setopt($curlSES,CURLOPT_URL,"$HASSIO_URL/config");
	curl_setopt($curlSES,CURLOPT_RETURNTRANSFER,true);
	curl_setopt($curlSES, CURLOPT_HTTPHEADER, array(
		'content-type: application/json',
		"Authorization: Bearer $SUPERVISOR_TOKEN"
	));
	
	$result = json_decode( curl_exec($curlSES) );
	curl_close($curlSES);
	return $result->time_zone;
}

function load_data() {
	global $json_folder;
	$sched = array();
	$filter = "*.json";
	$filelist = glob($json_folder.$filter);
	foreach ($filelist as $f) {
		$content = file_get_contents($f);
		$sched[] = json_decode($content);
	}
	return $sched;
	
}

function delete_file(string $id) {
	global $json_folder;
	$filename = $json_folder.$id.".json";	
	unlink ($filename);
	return $filename;
}

function create_file(string $eid) {
	global $json_folder;
	$on_dow="";
	$off_dow="";
	$id = ($eid!="") ? $eid : uniqid();
	$filename = $json_folder.$id.".json";
	if ($_POST['on_dow']) foreach($_POST['on_dow'] as $v) $on_dow.= $v;
	if ($_POST['off_dow']) foreach($_POST['off_dow'] as $v) $off_dow.= $v;
	foreach($_POST['entity_id'] as $e) $entity_id_array[]=$e;
	
	$item = new stdClass();	
	$item->id = $id;
	$item->name      = $_POST["name"];
	$item->enabled   = $_POST["enabled"];
	$item->entity_id = $entity_id_array; 
	$item->on_tod 	 = $_POST["on_tod"];
	$item->on_dow    = $on_dow;
	$item->off_tod 	 = $_POST["off_tod"];
	$item->off_dow 	 = $off_dow;
	file_put_contents($filename, json_encode($item));
	
	return $filename;
}

function get_events_array(string $s) {
	$trim_space = trim(preg_replace('/\s+/', ' ',$s));
	$list=explode(" ",$trim_space);
	asort($list);
	return $list;
}

function get_html_events_list(string $s) {
	$elist = get_events_array($s);
	$result ="";
	foreach ($elist as $e) $result .="<span>$e</span>";
	return $result;
}

function save_sort() {
	global $json_folder;
	$filename = $json_folder."sort.dat";
	
	$item = new stdClass();	
	$item->id_order = $_GET['list'];
	file_put_contents($filename, json_encode($item));
	
	return $filename;
}

function get_order_array() {
	global $json_folder;
	$ret_array=Array();
	$i=0;
	$filename = $json_folder."sort.dat";
	if (file_exists($filename)){
		$item = json_decode(@file_get_contents($filename));
		if (isset($item->id_order)) {
			foreach($item->id_order as $key=>$value) { $ret_array["$value"]=$key; }
		 }
	}
	return $ret_array;
}

function get_friendly_html_dow(string $s,bool $on) {
	global $weekdays;
	$html = "<div>";
	$onOffClass = ($on) ? "dowHiglightG" : "dowHiglightR";
	for($i=1; $i<=7; $i++) {
		$d = mb_substr($weekdays[$i],0,2);
		$class = (strpos($s, chr($i+48)  ) !== false ) ? $onOffClass : "" ;
		$html .= "<div class=\"dowIcon $class \" >$d</div> ";
	}
	$html .= "</div>";
	return $html;
	
}

function get_switch_html_select_options() {	
	$html = "";
	$switch_list = get_switch_list();	
	$comp="";
	foreach ($switch_list as $s) {
		$c = explode('.',$s->entity_id); 
		if ($comp!=$c[0]) {
			if ($comp!="") $html .= '</optgroup>';
			$comp=$c[0];
			$html .= '<optgroup label="' . $comp . '">';
		}
		$name = ($s->friendly_name=="") ? $s->entity_id : "$s->friendly_name ($s->entity_id)" ;
		$html .= "<option value=\"$s->entity_id\">$name</option>";
	}
	$html .= '</optgroup>';
	return $html;
}

function is_checked(string $s , int $i) {
	$checked = "checked";
	if (strpos($s, chr($i+48)  ) === false ) $checked = "";
	return $checked;
}

function get_sunset_sunrise() {
	global $sun_filename;
	global $sun_file_age;
	$result = array("sunset"=>"","sunrise"=>"",);
	
	if (!file_exists($sun_filename))  get_switch_list();
	if ( (time()-filemtime($sun_filename) ) > $sun_file_age ) get_switch_list();

	$json=json_decode(@file_get_contents($sun_filename));
	$sunset_timestamp = strtotime($json->next_setting);
	$sunrise_timestamp = strtotime($json->next_rising);
	$result["sunset"] = date("H:i",$sunset_timestamp);
	$result["sunrise"] = date("H:i",$sunrise_timestamp);
	
	return $result;
 }
 
 function save_sunset_sunrise(array $json) {
	global $sun_filename;
	global $sun_file_age;
	foreach ($json as $item) : 
	if ($item->entity_id == "sun.sun") :
		$attr = $item->attributes;
		break;
	endif;
	endforeach;
	
	try {	

		if (file_exists($sun_filename)) {
			if ( (time()-filemtime($sun_filename) ) > $sun_file_age ) file_put_contents( $sun_filename,json_encode($attr) );
		} else {
			@file_put_contents( $sun_filename,json_encode($attr) );
		}
	} catch (Exception $e) {
		if ($options->debug) echo 'Caught exception: ',  $e->getMessage(), "\n";
	}	

 }
 
 function is_scheduler_running() {
	$response=0;
	try {
		exec("pgrep -af scheduler", $pids);
		foreach ($pids as $p) {		if (strpos($p,"scheduler.php")!== false) $response=1; }
	} catch (Exception $e) {
		if ($options->debug) echo 'Caught exception: ',  $e->getMessage(), "\n";
	}		
	return $response ;
 }