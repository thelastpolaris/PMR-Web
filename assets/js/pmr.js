'use strict';

var GenerateToken = (function() {
	
	var $gen_token = $('#generate-token');

	$("#generate-token").click(function(){
    	$.post("/user",
    	{
            generate_token: true,
        },
        function(data, status){
    		$("#display-token").html(data)
  		});
	});

	// // Variables

	// var $datepicker = $('.datepicker');


	// // Methods

	// function init($this) {
	// 	var options = {
	// 		disableTouchKeyboard: true,
	// 		autoclose: false
	// 	};

	// 	$this.datepicker(options);
	// }


	// // Events

	// if ($datepicker.length) {
	// 	$datepicker.each(function() {
	// 		init($(this));
	// 	});
	// }

})();