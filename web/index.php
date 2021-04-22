<?php

	include_once("lib.php");

	if ( isset($_POST["action"]) ) {
		switch ($_POST["action"]) {
			case "update":
					create_file($_POST["id"]);
					break;
			case "new":
					create_file("");
					break;					
			case "delete":
					delete_file($_POST["id"]);
					break;		
				
		}					
	
		header("HTTP/1.1 303 See Other");
		header("Location: index.php");

	}
	
	if ( isset($_GET["action"]) ) {
		switch ($_GET["action"]) {
			case "status":
					echo is_scheduler_running();
					die();
			case "log":
					if (file_exists($logfile)) readfile($logfile); 
					die();	
			case "sort":
					save_sort();
					die;						
		}
	}					
	
	$wd=0;
	$sched = load_data();
	$select_option = get_switch_html_select_options();
	$sun = get_sunset_sunrise();
	$order_array=get_order_array();
	$order=0;
	
	
?>

<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Home Assistant Simple Scheduler</title>
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<link rel="stylesheet" href="https://cdn.materialdesignicons.com/4.8.95/css/materialdesignicons.min.css" >
<link href="//maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
<script src="//maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js" integrity="sha256-T0Vest3yCU7pafRw9r+settMBX6JkKN06dqBnpQ8d30=" crossorigin="anonymous"></script>
<script src="script.js" ></script>
<link rel="stylesheet" href="style.css" >
</head>
<body>

<div class="wrapper">

    <nav id="sidebar">
		<button type="button" aria-label="Close" class="btn btn-outline-secondary btn-sm" onclick="toggle_sidebar();">>>></button>
		
        <div id="sidebar-wrapper">
            ...
        </div>		
    </nav>		
	
          <div class="content">
			
							<div >
								<table class="table table-hover" id="dtable">
									<thead class="bg-primary">
									<tr>
									  <th scope="col">&nbsp;</th>
									  <th scope="col"><?php echo $translations->text_device; ?></th>
									  <th scope="col"><?php echo $translations->text_ON; ?></th>
									  <th scope="col"><?php echo $translations->text_OFF; ?></th>
									  <th scope="col"></th>
									</tr>
									</thead>
									<tbody>	
																				
										<?php foreach ($sched as $s) :  ?>
										<?php if ( !is_array($s->entity_id) ) {	$tmp = $s->entity_id; $s->entity_id = Array($tmp);	}	?>
										  <?php if ($s->id) :  ?>
											<?php $order= (isset($order_array[$s->id])) ? $order_array[$s->id] : 0 ;  ?>
											  <tr data-value="<?php echo $s->id ?>" data-order="<?php echo $order ?>" style="opacity: <?php echo ($s->enabled) ? "1" : ".3" ?>">
												  <td class="text-center"></td>
												  <td>
													<?php if (!isset($s->name) || $s->name =="" ) $s->name=$s->id; ?>
													<div class="row-title"><h5><?php echo $s->name ?></h5></div>
													
													<div>
													<?php foreach ( $s->entity_id as $e ) : ?>
														<span class="badge bg-primary" data-bs-toggle="tooltip" data-bs-html="true"  title="<?php echo $e ?>" ><?php echo ($switch_friendly_name[$e]=="") ?  $e : $switch_friendly_name[$e] ; ?></span>
													<?php endforeach; ?>
													</div>
												  </td>
												  <td class="text-green event-cell">
														<div class="event-list"><?php echo get_html_events_list($s->on_tod); ?></div>
														<?php if ($s->on_dow!="") echo get_friendly_html_dow($s->on_dow,true);  ?>
												  </td>
												  <td class="text-red event-cell">
														<div class="event-list"><?php echo get_html_events_list($s->off_tod); ?></div>
														<?php if ($s->off_dow!="") echo get_friendly_html_dow($s->off_dow,false);  ?>
												  </td>
												  <td><button type="button" class="btn btn-default bg-primary edit-button" aria-id="<?php echo $s->id ?>" ><span class="mdi mdi-pencil" ></span></button></td>
											  </tr>
										  <?php endif;  ?>
										<?php endforeach;  ?>
									</tbody>
								</table>
							</div>
							

							
            </div>
 
	 
	<button type="button" class="btn btn-default btn-circle btn-xl bg-primary floating-bottom-right add-button"><span class="mdi mdi-plus"></span> </button>  
    
	<div class="overlay"></div>		  
	
	<footer class="footer">
      <div class="statusbar">
        <p>
			<span>Scheduler:</span> <span class="statusbar_span" id="schedulerstatus"><?php echo (is_scheduler_running()) ? "" : "NOT " ?>RUNNING</span>
			<span class="statusbar_span"><?php echo "Sunrise ".$sun["sunrise"] ?></span>
			<span class="statusbar_span"><?php echo "Sunset ".$sun["sunset"] ?></span>
			<span class="statusbar_span"><?php echo "TZ: ".get_ha_timezone(); ?></span>
		</p>
      </div>
    </footer>

</div>

<script>
	$(document).on('click', '#addRow', function () {		
			var html = '';
			html += '<div id="inputFormRow">';
			html += '<div class="input-group mb-3">';
			html += '<select name="entity_id[]" class="form-control"><?php echo $select_option ?></select>';
			html += '<div class="input-group-append"><button id="removeRow" type="button" class="btn btn-danger"><span class="mdi mdi-delete" ></span></button></div>';
			html += '</div>';
			html += '</div>';
			$("#info").html('Clic ADD');
			$('.indexInput').append(html);
	});
</script>
</body>
</html>