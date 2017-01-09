$(function() {
	/* we know it's a boy...
  	if($('#radio1').is(':checked')) {
	   	$('.gender-g').removeClass('girl');
	   	$('.gender-b').addClass('boy');
	   	$('body').removeClass('gb');
	   	$('body').addClass('bb');
	   }
	   if($('#radio2').is(':checked')) {
	   	$('.gender-b').removeClass('boy');
	   	$('.gender-g').addClass('girl');
	   	$('body').removeClass('bb');
	   	$('body').addClass('gb');
	   }

	$('#gender').click(function() {
	   if($('#radio1').is(':checked')) {
	   	$('.gender-g').removeClass('girl');
	   	$('.gender-b').addClass('boy');
	   	$('body').removeClass('gb');
	   	$('body').addClass('bb');
	   }
	   if($('#radio2').is(':checked')) {
	   	$('.gender-b').removeClass('boy');
	   	$('.gender-g').addClass('girl');
	   	$('body').removeClass('bb');
	   	$('body').addClass('gb');
	   }
	});
	*/
	$(function() {
      // get page height and adjust
      var wh = $(window).height();
      var con = $('#mc').height();
      if (wh > con) {
        $('#mc').css({'height':(($(window).height())-80)+'px'});
      }
    });
});