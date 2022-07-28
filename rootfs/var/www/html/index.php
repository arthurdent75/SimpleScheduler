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
			case "dirt":
					get_dirt();
					die;
			case "setdirt":
					set_dirt();
					die;
			case "setstate":
					$id = $_GET["id"];
					$v = (bool) $_GET["v"];
					change_state_in_json_file($id,$v);	
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

	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@6.5.95/css/materialdesignicons.min.css" >
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">
	<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
	<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns" crossorigin="anonymous"></script>
	<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js" integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU=" crossorigin="anonymous"></script>
 
 
<style>
<?php include_once("light.css"); ?>
<?php if ($options->dark_theme) include_once("dark.css"); ?>
<?php if ($options->details_uncovered) echo "	.week_table{ display: table;}"; ?>
</style>
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
		<div>
			<table class="table table-hover" id="dtable">
				<thead class="bg-primary">
				<tr>
				  <th scope="col" colspan="4" ><h5>SimpleScheduler<H5></th>
				</tr>
				</thead>
				<tbody>	
					<?php foreach ($sched as $s) :  ?>
					<?php if ( !is_array($s->entity_id) ) {	$tmp = $s->entity_id; $s->entity_id = Array($tmp);	}	?>
						<?php if ($s->id) :  ?>
						  <?php $order= (isset($order_array[$s->id])) ? $order_array[$s->id] : 0 ;  ?>
							<?php if (isset($s->weekly)) :  ?>
								<?php $week_onoff = (array) $s->weekly; ?>
								<tr data-value="<?php echo $s->id ?>" data-order="<?php echo $order ?>" style="opacity: <?php echo ($s->enabled) ? "1" : ".3" ?>">

								  <td class="text-center drag_icon fit"> <span class="mdi mdi-calendar-range mdi-24px" ></span> </td>

								  <td class="text-center fit" >
									<button type="button" class="btn btn-default bg-primary edit-button" aria-id="<?php echo $s->id ?>" ><span class="mdi mdi-pencil" ></span></button>
									&nbsp;
									<button type="button" class="btn btn-default bg-primary view-button" aria-id="<?php echo $s->id ?>" ><span class="mdi mdi-eye" ></span></button>
								  </td>

								  <td  class="name_col" >
									<?php if (!isset($s->name) || $s->name =="" ) $s->name=$s->id; ?>
									<div class="row-title"><h5><?php echo $s->name ?></h5></div>
							
									<div class="entities_list">
									<?php foreach ( $s->entity_id as $e ) : ?>
										<span class="badge bg-primary" data-bs-toggle="tooltip" data-bs-html="true"  title="<?php echo $e ?>" ><?php echo ($switch_friendly_name[$e]=="") ?  $e : $switch_friendly_name[$e] ; ?></span>
									<?php endforeach; ?>
									</div>
								  </td>

								  <td>
										<div class="week_table w_mode" id="detail_<?php echo $s->id ?>">
											<div class="week_table_row week_table_header">
												<div class="week_table_cell"></div>
												<?php for($i=1; $i<=7; $i++) {
													   echo "<div class=\"week_table_cell\" style=\"width: 13.5%;\" >";																	   
													   echo	mb_substr($weekdays[$i],0,2); 
													   echo "</div>";
												} ?>
											</div>
											<div class="week_table_row text-green week_table_row_bottom_line">
												<div class="week_table_cell "><span class="badge  dowHiglightG "><?php echo $translations->text_ON; ?></span></div>
												<?php for($i=1; $i<=7; $i++) {
													   echo "<div class=\"week_table_cell\">";																		   
													   echo get_html_events_list($week_onoff["on_$i"],true); 
													   echo "</div>";
												} ?>
											</div>
											<div class="week_table_row text-red week_table_row_bottom_line">
												<div class="week_table_cell "><span class="badge  dowHiglightR "><?php echo $translations->text_OFF; ?></span></div>
												<?php for($i=1; $i<=7; $i++) {
													   echo "<div class=\"week_table_cell\">";
													   echo get_html_events_list($week_onoff["off_$i"],false);																		   
													   echo "</div>";
												} ?>
											</div>																
										</div>	
								  </td>
							  </tr>
							<?php else:  ?>
							  <tr data-value="<?php echo $s->id ?>" data-order="<?php echo $order ?>" style="opacity: <?php echo ($s->enabled) ? "1" : ".3" ?>">

								  <td class="text-center drag_icon fit"><span class="mdi mdi-calendar-week mdi-24px" ></span></td>

								  <td class="text-center fit" >
									<button type="button" class="btn btn-default bg-primary edit-button" aria-id="<?php echo $s->id ?>" ><span class="mdi mdi-pencil" ></span></button>
									&nbsp;
									<button type="button" class="btn btn-default bg-primary view-button" aria-id="<?php echo $s->id ?>" ><span class="mdi mdi-eye" ></span></button>
								  </td>

								  <td  class="name_col" >
									<?php if (!isset($s->name) || $s->name =="" ) $s->name=$s->id; ?>
									<div class="row-title"><h5><?php echo $s->name ?></h5></div>
									
									<div class="entities_list">
									<?php foreach ( $s->entity_id as $e ) : ?>
										<span class="badge bg-primary" data-bs-toggle="tooltip" data-bs-html="true"  title="<?php echo $e ?>" ><?php echo ($switch_friendly_name[$e]=="") ?  $e : $switch_friendly_name[$e] ; ?></span>
									<?php endforeach; ?>
									</div>
								  </td>

								  <td class="event-cell">
										<div class="week_table d_mode"  id="detail_<?php echo $s->id ?>">
											<div class="week_table_row ">
												<div class="week_table_cell ">
													<div class="event-list text-green"><?php echo get_html_events_list($s->on_tod); ?></div>
													<div style="clear:both;"></div>
													<?php if ($s->on_dow!="") echo get_friendly_html_dow($s->on_dow,true);  ?>
												</div>									
												<div class="week_table_cell ">
													<div class="event-list text-red"><?php echo get_html_events_list($s->off_tod,false); ?></div>
													<div style="clear:both;"></div>
													<?php if ($s->off_dow!="") echo get_friendly_html_dow($s->off_dow,false);  ?>
												</div>									
											</div>									
										</div>									
								  </td>
							  </tr>
							<?php endif;  ?>
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
			<span class="statusbar_span"><?php echo "Sunrise ".$sun["sunrise"] ?></span>
			<span class="statusbar_span"><?php echo "Sunset ".$sun["sunset"] ?></span>
			<span class="statusbar_span"><?php echo "TZ: ".get_ha_timezone(); ?></span>
			<span>Scheduler:</span> <span class="statusbar_span" id="schedulerstatus"><?php echo (is_scheduler_running()) ? "" : "NOT " ?>RUNNING</span>
		</p>
      </div>
    </footer>

</div>

<script>

	$( document ).ready(function() {
		
			var $tbody = $("#dtable tbody");
			
			$tbody.sortable({
				distance: 5,
				delay: 100,
				opacity: 0.6,
				cursor: 'move',
				update:  function(e, tr) {
							var orderlist = '';
							$('tr.ui-sortable-handle').each(function (i) {
								$(this).attr('data-order',i);
								orderlist=orderlist+'&list['+i+']='+$(this).attr('data-value');
							});
							$("#sidebar-wrapper").load("index.php?action=sort"+orderlist);
						}
			}).disableSelection();
			
			
			$tbody.find('tr.ui-sortable-handle').sort(function (a, b) {
				var tda = parseInt($(a).attr('data-order')); 
				var tdb = parseInt($(b).attr('data-order')); 
				return tda > tdb ? 1
					   : tda < tdb ? -1
					   : 0;
			}).appendTo($tbody);
			
	
	});	
	
	$(document).on('click', '.edit-button', function () {
			v=$(this).attr('aria-id');
			$("#sidebar-wrapper").html('');
			$("#sidebar").show();
			$("body").css('overflow','hidden');
            $("#sidebar-wrapper").load("edit.php?id="+v, function() {
				$(".entity-dropdown-fix").each(function( t ) {
					  this.value = $(this).attr('aria-data');
					});
				});
    });  
	
	$(document).on('click', '.view-button', function () {
			var v=$(this).attr('aria-id');
			var t="#detail_"+v;
			if ($(t).css('display')=="table") {
				$(t).css('display','none');
			}else{
				$(t).css('display','table');
			}
    });  	

	$(document).on('click', '.add-button', function () {
			$("#sidebar-wrapper").html('');
			$("#sidebar").show();
            $("#sidebar-wrapper").load("new.php");
    }); 
	
	$(document).on('click', '.img-add-new', function () {
			v=$(this).attr('aria-id');
			$("#sidebar-wrapper").html('');
			$("#sidebar").show();
            $("#sidebar-wrapper").load("edit.php?id="+0+"&type="+v);
    }); 	
	
	$(document).on('click', '.delete-button', function () {
			var f = document.getElementById("edit-form");
			if (window.confirm("Are you sure?")) {
				f.action.value="delete"; 
				f.submit(); 
			}
    }); 	
		
	$(document).on('click', '#removeRow', function () {
			$(this).closest('#inputFormRow').remove();
	});  		
	

	
	function toggle_sidebar(){
		$("#sidebar").hide();
		$("body").css('overflow','auto');
	}
	
</script>

<script>

	var intervalcheck = window.setInterval(function(){
		$.get("?action=dirt", function( r ) {
			if (r=="1") location.reload();
		});
	}, 5000);

	$(document).on('click', '#addRow', function () {		
			var html = '';
			html += '<div id="inputFormRow">';
			html += '<div class="input-group mb-3">';
			html += '<select name="entity_id[]" class="form-control"><?php echo addslashes($select_option); ?></select>';
			html += '<div class="input-group-append"><button id="removeRow" type="button" class="btn btn-danger"><span class="mdi mdi-delete" ></span></button></div>';
			html += '</div>';
			html += '</div>';
			$("#info").html('Clic ADD');
			$('.indexInput').append(html);
	});
</script>

</body>
</html>
