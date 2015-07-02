( function (G, U) {

  	var FormHelper = G.FurnFormHelper || {};

  	var init = function() {

		var $rangeFrom = $("#id_range_from").parents('.form-group'); 
		var $rangeTo = $("#id_range_to").parents('.form-group');

		function refreshDateRangeControls() {
			if($("#id_date_range").val() === 'custom') {
			  $rangeFrom.show();
			  $rangeTo.show(); 
			} else {
			  $rangeFrom.hide();
			  $rangeTo.hide(); 
			  $rangeFrom.find('input').val('');
			  $rangeTo.find('input').val('');
			}
		}
		
		refreshDateRangeControls();
		$("#id_date_range").on('change', function (){
			refreshDateRangeControls();
		});
			
	}

	FormHelper.init = init;
  	G.DateRangeFormHelper = FormHelper;

}(this, undefined))	  	