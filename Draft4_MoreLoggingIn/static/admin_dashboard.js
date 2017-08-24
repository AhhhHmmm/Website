$(document).ready(function() {
	$('.nav-sidebar > li').each(function() {
		$(this).on('click', function(event) {
			$('.active').removeClass('active');
			$(this).addClass('active');
		});
	});
});