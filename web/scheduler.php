<?php

	echo "\n\nStarting...\n";
	
	include_once("lib.php");

	while(true) :
	
		$seconds = date("s");

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
						
echo "ON    \n ";
					if (strpos($s->on_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->on_tod);
						foreach($elist as  $e) :
							$extra = ""; $value = "";
							$event_time = evaluate_event_time($e,$sun);
echo "$event_time ";
							if ( $event_time==$current_time ) :
								$extra = get_event_extra_info($e);
								$value=$extra[1] ;
								call_HA($s->entity_id,"on",$value);
							endif;								
						endforeach;
echo "\n ";
					endif;
					
echo "OFF    \n ";
					if (strpos($s->off_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->off_tod);
						foreach($elist as  $e) :
							$event_time = evaluate_event_time($e,$sun);
echo "$event_time ";							
							if ( $event_time==$current_time ) call_HA($s->entity_id,"off");					
						endforeach;
echo "\n ";						
					endif;
					
				endif;
				
			endforeach;
			
		endif;
		
		sleep(1);
		
	endwhile;