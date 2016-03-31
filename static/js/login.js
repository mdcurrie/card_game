$(function() {
	$('#container').fadeIn(400, function() {
		$('input[type="text"]').focus();
	});

	$('form').submit(function(e) {
		e.preventDefault();
		var name = $('input[type="text"]').val();
		if (/^[a-z0-9]+$/i.test(name) && name.length >=5) {
			$('#container').fadeOut(400, function() {
				$('form').unbind('submit').submit();
			});
		}
		else
			$('div span').hide().text('Name must be at least five alphanumeric characters.').fadeIn(400);
	});
});