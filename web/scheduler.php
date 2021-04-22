<?php

	echo "Starting...\n";
	
	include_once("lib.php");

	while(true) :
	
		$seconds = date("s");

		if ($seconds=="00") :
			
			$current_time = date("H:i");
			$current_dow = date("N");
			
			$sun = get_sunset_sunrise();
			$is_sunset  = (bool)($current_time==$sun["sunset"]);
			$is_sunrise = (bool)($current_time==$sun["sunrise"]);
			
			$sched = load_data();
			
			foreach ($sched as $s) :
		
				if ($s->enabled):
				
					if (strpos($s->on_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->on_tod);
						foreach($elist as  $e) :
							if ( $e==$current_time  ) call_HA($s->entity_id,"on");
							if ( strtolower($e)=="sunset"  && $is_sunset   ) call_HA($s->entity_id,"on");
							if ( strtolower($e)=="sunrise" && $is_sunrise  ) call_HA($s->entity_id,"on");
						endforeach;
					endif;
					
					if (strpos($s->off_dow,  $current_dow)!== false) :
						$elist = get_events_array($s->off_tod);
						foreach($elist as  $e) :					
							if ( $e==$current_time  ) call_HA($s->entity_id,"off");					
							if ( strtolower($e)=="sunset"  && $is_sunset  ) call_HA($s->entity_id,"off");
							if ( strtolower($e)=="sunrise" && $is_sunrise ) call_HA($s->entity_id,"off");
						endforeach;
					endif;
					
				endif;
				
			endforeach;
			
		endif;
		
		sleep(1);
		
	endwhile;