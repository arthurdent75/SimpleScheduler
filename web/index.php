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

<link rel="stylesheet" href="https://cdn.materialdesignicons.com/5.4.55/css/materialdesignicons.min.css" >
<link href="//maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
<script src="//maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js" integrity="sha256-T0Vest3yCU7pafRw9r+settMBX6JkKN06dqBnpQ8d30=" crossorigin="anonymous"></script>

<style>

	#sidebar {
		display:none;
		min-width: 250px;
		max-width: 25%;
		height: 100%;
		position: fixed;
		top: 0;
		right: 0;
		padding: 1em;
		z-index: 9999;
		background-color: rgba(255,255,255,0.98);
		box-shadow: 5px 5px 18px 0px #000;	
	}

	.edit-form > div {
		margin: 1em 0;
	}

	.btn-default { color: white;}

	.dowIcon  {
		border: 0px solid ;
		border-radius: 20px;
		background: grey;
		color: white;
		font-size: 1rem;
		width: 2rem;
		height: 2rem;
		line-height: 2rem;
		text-align: center;
		margin-right: 0.1em;
		display: inline-block
	}

	.dowHiglightR { 	background: red ; }
	.dowHiglightG { 	background: green ; }

	.icon-space {width: 32px;}

	.text-green {color:green;}
	.text-red   {color:red;}
	.text-white   {color:white;}

	.bg-primary  {color:white;}



	div.edit-section-label {
		width: 100%;
		border-bottom: 1px solid #777;
		margin-top: 1em;
	}
	div.edit-section-label label{
		line-height: 1em;
		font-weight: bold;
	}

	.btn-circle.btn-xl {
		width: 70px;
		height: 70px;
		padding: 10px 16px;
		border-radius: 35px;
		font-size: 24px;
		line-height: 1.33;
	}

	.btn-circle {
		width: 30px;
		height: 30px;
		padding: 6px 0px;
		border-radius: 15px;
		text-align: center;
		font-size: 12px;
		line-height: 1.42857;
		background: navy;
		color: white;
		box-shadow: 2px 2px 10px 0px #777;
	}

	.floating-bottom-right {
		position: fixed;
		bottom: 5%;
		right: 5%;
	}

	.table td, .table th {
		vertical-align: middle;
		
	}

	.event-list > span {
		font-weight: bold;
		font-size: 1.25rem;
		margin-right: 1rem;
		line-height: 2rem;
	}

	span.event-type-b {
		font-size: 1rem;
		color: #d39e00;
		margin-left: 0.2rem;
		font-weight: normal;
	}

	span.event-type-t {
		font-size: 1rem;
		color: #795548;
		margin-left: 0.1rem;
		font-weight: normal;
	}


	footer {
		position: fixed;
		bottom: 0;
		right: 0;
		margin:0;
		padding: 0;
		width: 100%;
		height: 2em;
		line-height: 2em;
		font-size: 0.8em;
		background-color: grey;
		color: white;
	}

	footer .statusbar {
		margin-left: 1em;
	}

	.statusbar_span {margin-right: 2em;}

	@media screen and (min-width: 1281px) {
		html {	font-size: 10pt; }
	}

	@media screen and (max-width: 1280px) {
		html {	font-size: 9pt; }
	}

	@media screen and (max-width: 800px) {
		
	html {	font-size: 8pt; }

	TABLE TD {
		display: block;
		text-align: center;
		border: none !important;
	}

	TABLE TD:first-child {display:none;}
	TABLE TD:nth-child(2) {

	}

	TABLE TR {
		box-shadow: 0px -10px 20px -10px #777;
	}

	TABLE THEAD {
		display: none;
	}

	}

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
								// console.log(i, $(this).attr('data-order') , $(this).attr('data-value') );
								$(this).attr('data-order',i);
								orderlist=orderlist+'&list['+i+']='+$(this).attr('data-value');
							});
							// console.log(orderlist);
							$("#sidebar-wrapper").load("index.php?action=sort"+orderlist);
						}
			}).disableSelection();
			
			
			$tbody.find('tr.ui-sortable-handle').sort(function (a, b) {
				var tda = $(a).attr('data-order'); 
				var tdb = $(b).attr('data-order'); 
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

	$(document).on('click', '.add-button', function () {
			$("#sidebar-wrapper").html('');
			$("#sidebar").show();
            $("#sidebar-wrapper").load("edit.php?id="+0);
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
</body>
</html>