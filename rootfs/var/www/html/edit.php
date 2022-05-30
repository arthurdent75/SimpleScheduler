<?php 	

	include_once("lib.php");
	
	if ( !isset($_GET["id"]) ) die();
	if ( isset($_GET["type"]) ) $type=$_GET["type"];
	
	$id=$_GET["id"];

	if ($id==0) {
			if ($type=='D') $s = json_decode('{"id":"","name":"","enabled":"1","entity_id":[""],"on_tod":"","on_dow":"","off_tod":"","off_dow":""}');
			if ($type=='W') $s = json_decode('{"id":"","name":"","enabled":"1","entity_id":[""],"weekly":{"on_1":"","on_2":"","on_3":"","on_4":"","on_5":"","on_6":"","on_7":"","off_1":"","off_2":"","off_3":"","off_4":"","off_5":"","off_6":"","off_7":""}}');
		} else {
			$jsonFile=$json_folder . $id . ".json";
			$s = json_decode(file_get_contents($jsonFile));
	}
	$select_option = get_switch_html_select_options();


	
	if ( !isset($s->name) |  $s->name =="" ) $s->name=$s->id;
	if ( !is_array($s->entity_id) ) {
		$tmp = $s->entity_id;
		$s->entity_id = Array($tmp);
	}	
?>

	   <div>
				<div>
					<form  id="edit-form" class="edit-form" action="index.php" method="post"  >
					 <input type="hidden" name="id" value="<?php echo $s->id ?>" >
					 <input type="hidden" name="action" value="update" >
					 
						
						<div class="edit-section-label"><label><?php echo $translations->text_name; ?></label></div>
						<div>
							<input type="text" name="name" class="form-control input-sm" placeholder="<?php echo $translations->text_name; ?>" value="<?php echo $s->name ?>">
						</div>
						<div>
							<label class="checkbox-inline"><input type="checkbox" name="enabled" value="1" <?php echo ($s->enabled) ? "checked" : "" ; ?> > <?php echo $translations->text_enabled; ?></label>
						</div>
							
						<div class="edit-section-label"><label><?php echo $translations->text_device; ?></label></div>
						<div class="indexInput">
							<?php foreach ( $s->entity_id as $e ) : ?>
								<div id="inputFormRow">							
									<div class="input-group mb-3">
										<select name="entity_id[]" aria-data="<?php echo $e; ?>" class="form-control entity-dropdown-fix"><?php echo $select_option ?></select>
										<div class="input-group-append"><button id="removeRow" type="button" class="btn btn-danger"><span class="mdi mdi-delete" ></span></button></div>
									</div>
								</div>
							<?php endforeach; ?>
						</div>
						
						<div>
							<button id="addRow" type="button" class="btn btn-info addRow">+</button>
						</div>
						
					<?php if (isset($s->weekly)) : ?>	
						<input type="hidden" name="type" value="weekly" >
						<div class="edit-section-label"><label><?php echo $translations->text_ON." / ". $translations->text_OFF ; ?></label></div>
						<?php $week_onoff = (array) $s->weekly; ?>
								<table>
									<tr>
										<td></td>
										<td><?php echo $translations->text_ON; ?></td>
										<td><?php echo $translations->text_OFF; ?></td>
									</tr>
								  <?php for($i=1; $i<=7; $i++) : ?>
									<tr>
										<td><?php echo	mb_substr($weekdays[$i],0,2); ?></td>
										<td><input type="text" name="<?php echo "on_$i"; ?>" class="form-control input-sm" value="<?php echo $week_onoff["on_$i"] ?>"></td>
										<td><input type="text" name="<?php echo "off_$i"; ?>" class="form-control input-sm" value="<?php echo $week_onoff["off_$i"] ?>"></td>
									</tr>
								  <?php endfor; ?>
								</table>
								
					<?php else : ?>
						<input type="hidden" name="type" value="daily" >
								<div class="edit-section-label"><label><?php echo $translations->text_ON; ?></label></div>
								<div>
									<input type="text" name="on_tod" class="form-control input-sm" value="<?php echo $s->on_tod ?>">
								</div>
								
								<div>
									<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
										<label class="checkbox-inline"><input type="checkbox" name="on_dow[]" value="<?php echo $wd; ?>" <?php echo is_checked($s->on_dow,$wd); ?> ><?php echo mb_substr($weekdays[$wd],0,2); ?></label>
									<?php endfor; ?>							
								</div>
								
								<div class="edit-section-label"><label><?php echo $translations->text_OFF; ?></label></div>
								<div>
									<input type="text" name="off_tod" class="form-control input-sm"  value="<?php echo $s->off_tod ?>">
								</div>
								
								<div>
									<?php for ($wd=1 ; $wd<=7; $wd++) : ?>
										<label class="checkbox-inline"><input type="checkbox" name="off_dow[]" value="<?php echo $wd; ?>" <?php echo is_checked($s->off_dow,$wd); ?> ><?php echo mb_substr($weekdays[$wd],0,2); ?></label>
									<?php endfor; ?>							
								</div>						
					<?php endif; ?>						

						<div>
							<!-- <button type="button" onclick="toggle_sidebar();" class="btn btn-default btn-circle bg-warning"><span class="mdi mdi-pencil-off" ></span></button> -->
							<button type="submit" class="btn btn-default bg-success float-left"><span class="mdi mdi-content-save" ></span> <?php echo $translations->text_save; ?> </button>
							<?php if ($id): ?>
							<button type="button" class="btn btn-default  bg-danger float-right delete-button" ><span class="mdi mdi-delete" ></span> </button>
							<?php endif; ?>
						</div>
						
					</form>
				  </div>	
	</div>
	<div style="clear:both;"></div>
	<br/>
