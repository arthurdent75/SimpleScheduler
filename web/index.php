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
	
	$wd=0;
	$sched = load_data();
	$select_option = get_switch_html_select_options();
?>

<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Home Assistant Simple Scheduler</title>
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<link rel="stylesheet" href="https://cdn.materialdesignicons.com/4.8.95/css/materialdesignicons.min.css" >
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
<script src="script.js" ></script>
<link rel="stylesheet" href="style.css" >
</head>
<body>

	<div class="table-responsive">
		<table class="table ">
			<thead class="thead-dark">
			<tr>
			  <th scope="col">&nbsp;</th>
			  <th scope="col"><?php echo $options->text_device; ?></th>
			  <th scope="col"><?php echo $options->text_ON; ?></th>
			  <th scope="col"></th>
			  <th scope="col"><?php echo $options->text_OFF; ?></th>
			  <th scope="col"></th>
			  <th scope="col"></th>
			</tr>
			</thead>
			<tbody>	
			  <tr id="rowFormNew" style="display:none" >
				<form class="form-inline" action="#"  method="post" >
			      <input type="hidden" name="action" value="new" >				
			      <input type="hidden" name="enabled" value="1" >				
					<td></td>
					<td><select name="entity_id" class="form-control"><?php echo $select_option ?></select></td>
					<td><input type="text" name="on_tod" class="form-control input-sm" placeholder="00:00"></td>
					<td>
						<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
							<label class="checkbox-inline"><input type="checkbox" name="on_dow[]" value="<?php echo $wd; ?>"><?php echo substr($weekdays[$wd],0,2); ?></label>
						<?php endfor; ?>
					</td>
					<td><input type="text" name="off_tod" class="form-control input-sm" placeholder="00:00"></td>
					<td>
						<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
							<label class="checkbox-inline"><input type="checkbox" name="off_dow[]" value="<?php echo $wd; ?>"><?php echo substr($weekdays[$wd],0,2); ?></label>
						<?php endfor; ?>					
					</td>							
					<td><button type="submit" class="btn btn-default" ><?php echo $options->text_save; ?></button></td>
				</form>
			  </tr>
								
				<?php foreach ($sched as $s) :  ?>
				  <tr id="rowShow_<?php echo $s->id ?>" style="opacity: <?php echo ($s->enabled) ? "1" : ".3" ?>">
					  <td class="text-center"><span class="mdi mdi-36px <?php echo ($s->enabled) ? "mdi-toggle-switch text-green" : "mdi-toggle-switch-off-outline"; ?> resize-icon" ></span></td>
					  <td><span id="select_<?php echo $s->id ?>" data-toggle="tooltip" data-placement="top" title="<?php echo $s->entity_id ?>"><strong><?php echo $switch_friendly_name[$s->entity_id] ?></strong></span></td>
					  <td class="text-green"><strong><?php echo $s->on_tod ?></strong></td>
					  <td><?php if ($s->on_dow!="") echo get_friendly_html_dow($s->on_dow,true);  ?></td>
					  <td class="text-red"><strong><?php echo $s->off_tod ?></strong></td>
					  <td><?php if ($s->off_dow!="") echo get_friendly_html_dow($s->off_dow,false);  ?></td>
					  <td><button type="button" onclick="showForm('<?php echo $s->id ?>')" class="btn btn-default btn-circle bg-primary"><span class="mdi mdi-pencil" ></span></button></td>
				  </tr>
				  
				  
				  <tr id="rowForm_<?php echo $s->id ?>" style="display:none"   >
					<form  id="form_<?php echo $s->id ?>" class="form-inline" action="#" method="post"  >
					 <input type="hidden" name="id" value="<?php echo $s->id ?>" >
					 <input type="hidden" name="action" value="update" >
						<td><label class="checkbox-inline"><input type="checkbox" name="enabled" value="1" <?php echo ($s->enabled) ? "checked" : "" ; ?> > <?php echo $options->text_enabled; ?></label></td>
						<td><select id="select_f_<?php echo $s->id ?>" name="entity_id"  class="form-control"><?php echo $select_option ?></select></td>
						<td><input type="text" name="on_tod" class="form-control input-sm" value="<?php echo $s->on_tod ?>"></td>
						<td>
							<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
								<label class="checkbox-inline"><input type="checkbox" name="on_dow[]" value="<?php echo $wd; ?>" <?php echo is_checked($s->on_dow,$wd); ?> ><?php echo substr($weekdays[$wd],0,2); ?></label>
							<?php endfor; ?>							
						</td>
						<td><input type="text" name="off_tod" class="form-control input-sm"  value="<?php echo $s->off_tod ?>"></td>
						<td>
							<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
								<label class="checkbox-inline"><input type="checkbox" name="off_dow[]" value="<?php echo $wd; ?>" <?php echo is_checked($s->off_dow,$wd); ?> ><?php echo substr($weekdays[$wd],0,2); ?></label>
							<?php endfor; ?>							
						</td>						
						<td>
							<button type="button" onclick="deleteRow('<?php echo $s->id ?>')" class="btn btn-default btn-circle bg-danger"><span class="mdi mdi-delete" ></span> </button>
							&nbsp;&nbsp;&nbsp;
							<button type="button" onclick="showForm('<?php echo $s->id ?>') " class="btn btn-default btn-circle bg-warning"><span class="mdi mdi-pencil-off" ></span></button>
							<button type="button" onclick="saveRow('<?php echo $s->id ?>')  " class="btn btn-default btn-circle bg-success"><span class="mdi mdi-content-save" ></span> </button>
						</td>
					</form>
				  </tr>
				  
				<?php endforeach;  ?>
			</tbody>
		</table>
	</div>
	
	<button type="button" onclick="showAddRow()" class="btn btn-default btn-circle btn-xl bg-primary floating-bottom-right"><span class="mdi mdi-plus"></span> </button>

</body>
</html>
