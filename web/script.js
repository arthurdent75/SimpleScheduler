

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
	

	
