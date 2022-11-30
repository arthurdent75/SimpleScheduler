<?php

	echo '[' . date('r') . "] Starting scheduler...\n";
	
	include_once("lib.php");
	
	$tz = get_ha_timezone();
	if ($tz) date_default_timezone_set($tz);
	echo '[' . date('r') . "] Home Assistant TimeZone: {$tz} \n";	
	
	$rtz = date_default_timezone_get();
	echo '[' . date('r') . "] Addon TimeZone: {$tz} \n";	
	
	$max_retry = $options->max_retry;
	
	$command_queue[] = Array();
			
	while(true) :
		
		$seconds = date("s");
		//echo "\n\r$seconds   \033[1A ";
		
		if ($seconds=="00") :
	
			$current_time = date("H:i");
			$current_dow = date("N");
			
			$sun = get_sunset_sunrise();
			
			$sched = load_data();
			
			foreach ($sched as $s) :
		
				if ($s->enabled):
					
					if ( !is_array($s->entity_id) ) { $tmp = $s->entity_id; $s->entity_id = Array($tmp); }
					
					if (isset($s->weekly)) {
						$week_onoff = (array) $s->weekly;
						$s->on_tod = $week_onoff["on_$current_dow"];
						$s->off_tod = $week_onoff["off_$current_dow"];
						$s->on_dow=$current_dow;
						$s->off_dow=$current_dow;
					}
						
					if (strpos($s->on_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->on_tod);
						foreach($elist as  $e) :
							$extra = ""; $value = "";
							$event_time = evaluate_event_time($e,$sun);
							if ( $event_time==$current_time ) :
								$extra = get_event_extra_info($e);
								$value=$extra[1] ;
								call_HA($s->entity_id,"on",$value);
								foreach ($s->entity_id as $ent_id):
										$cmd = new stdClass();
										$cmd->entity_id = $ent_id;
										$cmd->sched_id = $s->id;
										$cmd->state = 'on';
										$cmd->value = $value;
										$cmd->countdown = $max_retry;
										$command_queue[ uniqid()] = $cmd;
										unset($cmd);
								endforeach;
							endif;								
						endforeach;
					endif;
					
					if (strpos($s->off_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->off_tod);
						foreach($elist as  $e) :
							$event_time = evaluate_event_time($e,$sun);
							if ( $event_time==$current_time ) {
								call_HA($s->entity_id,"off");					
								foreach ($s->entity_id as $ent_id):
										$cmd = new stdClass();
										$cmd->entity_id = $ent_id;
										$cmd->sched_id = $s->id;
										$cmd->state = 'off';
										$cmd->value = "";
										$cmd->countdown = $max_retry;
										$command_queue[ uniqid()] = $cmd;
										unset($cmd);
								endforeach;	
							}
						endforeach;
					endif;
					
				endif;
				
			endforeach;
			
			sleep(5);
			
			unset($command_queue[0]);

			foreach ($command_queue as $key=>$value) :
				$entity_status = get_entity_status($value->entity_id);
				if ($entity_status!='unavailable') {
						unset($command_queue[$key]);
						if ($entity_status!=$value->state & $value->countdown < $max_retry ) {
								echo '[' . date('r') . "] SCHED:  {$value->entity_id} is available. \n";
								call_HA(array($value->entity_id),$value->state,$value->value);
						}
					} else {
						$attempt = 1 + (int)$max_retry - (int)$value->countdown ;
						echo '[' . date('r') . "] SCHED:  {$value->entity_id} is unavailable! Attempt $attempt of $max_retry \n";
						call_HA(array($value->entity_id),$value->state,$value->value);
						$command_queue[$key]->countdown--;
						if ($command_queue[$key]->countdown <=0) unset($command_queue[$key]);
				}
			endforeach;

		endif;
		
		sleep(1);
		
	endwhile;