<?php

	echo "Starting...\n";
	
	include_once("lib.php");

	date_default_timezone_set(get_ha_timezone());	
	
	while(true) :
	
		$seconds = date("s");

		if ($seconds=="00") :
			
			$current_time = date("H:i");
			$current_dow = date("N");

			$sched = load_data();
			
			foreach ($sched as $s) :
		
				if ($s->enabled):
					if ( $s->on_tod==$current_time  && strpos($s->on_dow,  $current_dow)!== false ) call_HA($s->entity_id,"on");
					if ( $s->off_tod==$current_time && strpos($s->off_dow, $current_dow)!== false ) call_HA($s->entity_id,"off");					
				endif;
				
			endforeach;
			
		endif;
		
		sleep(1);
		
	endwhile;
	
