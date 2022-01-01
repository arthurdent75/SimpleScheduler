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


function call_HA (Array $eid_list, string $action , string $value="" ) {

	global $HASSIO_URL;
	$result ="";
	
	foreach ($eid_list as $eid):
	
			$domain = explode(".",$eid);
			$command_url = $HASSIO_URL . "/services/" . $domain[0] . "/turn_" . $action;
			
			$postdata = "{\"entity_id\":\"$eid\"}" ;
			
			if ($domain[0]=="light" && $value!="" ) {
				$v = (int)((int)$value * 2.55);
				$postdata = "{\"entity_id\":\"$eid\",\"brightness\":\"$v\"}" ;
			}
			
			if ($domain[0]=="cover"  ) {
				if ( $value!=""  ) {
					$v = (int)$value ;
					$command_url = $HASSIO_URL . "/services/cover/set_cover_position";
					$postdata = "{\"entity_id\":\"$eid\",\"position\":\"$v\"}" ;
				} else {
					if ($action=="on" ) {
						$command_url = $HASSIO_URL . "/services/cover/open_cover";
						$postdata = "{\"entity_id\":\"$eid\"}" ;
					} else {
						$command_url = $HASSIO_URL . "/services/cover/close_cover";
						$postdata = "{\"entity_id\":\"$eid\"}" ;
					}
				}
			}			
			
			call_HA_API($command_url,$postdata);

			if ($domain[0]=="climate" && $value!="" ) {
				$command_url = $HASSIO_URL . "/services/climate/set_temperature";
				$postdata = "{\"entity_id\":\"$eid\",\"temperature\":$value}" ;
				call_HA_API($command_url,$postdata);
			}			

			$ts = date("Y-m-d H:i");
			echo "\n$ts --> Turning $action $eid";
			if ($domain[0]=="light" && $value!="" ) echo " at $value%";
			if ($domain[0]=="climate" && $value!="" ) echo " at ${value}°";
			if ($domain[0]=="cover" && $value!="" ) echo " at ${value}%";
			
	endforeach;
	
	return $result;
}

function call_HA_API (string $command_url , string $postdata ) {
			
			global $SUPERVISOR_TOKEN;
			
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
			return $foo;
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
	if (isset($_POST['on_dow']))  if ($_POST['on_dow']) foreach($_POST['on_dow'] as $v) $on_dow.= $v;
	if (isset($_POST['off_dow'])) if ($_POST['off_dow']) foreach($_POST['off_dow'] as $v) $off_dow.= $v;
	foreach($_POST['entity_id'] as $e) $entity_id_array[]=$e;
	$enabled = (isset($_POST["enabled"])) ? 1 : 0;
	$item = new stdClass();	
	$item->id = $id;
	$item->name      = $_POST["name"];
	$item->enabled   = $enabled;
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
	$remove_commas=str_replace( ',' , ' ' , $trim_space );
	$remove_commas=str_replace( ';' , ' ' , $remove_commas );
	$list=explode(" ",$remove_commas);
	asort($list);
	return $list;
}

function get_html_events_list(string $s,bool $showvalue=true) {
	$elist = get_events_array($s);
	$result ="";
	foreach ($elist as $e) {
		$extra="";
		$piece=explode(">",$e);
		if (isset($piece[1]) && $showvalue) {
			$v = substr(trim($piece[1]), 1);
			if(strtoupper($piece[1][0])=="B") $extra="<span class=\"event-type-b\"><i class=\"mdi mdi-lightbulb\" aria-hidden=\"true\"></i>$v%</span>";
			if(strtoupper($piece[1][0])=="T") $extra="<span class=\"event-type-t\"><i class=\"mdi mdi-thermometer\" aria-hidden=\"true\"></i>$v&deg;</span>";
			if(strtoupper($piece[1][0])=="P") $extra="<span class=\"event-type-p\"><i class=\"mdi mdi-arrow-up-down\" aria-hidden=\"true\"></i>$v%</span>";
		}
		$result .="<span>$piece[0]$extra</span>";
	}
	return $result;
}

function evaluate_event_time(string $e, array $sun) {
		$event="";
		$e=strtoupper($e);
		$piece=explode(">",$e);	
		$event=trim($piece[0]);
		$operator="~";
		
		if (substr($event,0,3)=="SUN") {
			if (strpos($event, '+') !== false) $operator="+";
			if (strpos($event, '-') !== false) $operator="-";
			$split=explode($operator,$event);
			if ($split[0]=="SUNSET") $event=$sun["sunset"];
			if ($split[0]=="SUNRISE") $event=$sun["sunrise"];
			if (isset($split[1])) {
				$offset=(int)$split[1];
				$event_time_format = strtotime("$event $operator $offset minute  ");
				$event = date("H:i", $event_time_format );
			}
		}
	return $event;
}

function get_event_extra_info(string $e) {
		$extra="";
		$t = "";
		$v = "";
		$piece=explode(">",$e);
		if (isset($piece[1])) {
			$t = substr(trim($piece[1]), 0,1);
			$v = substr(trim($piece[1]), 1);
		}	
		return Array($t,$v);
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