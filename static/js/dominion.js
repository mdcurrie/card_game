$(function() {
	$('#waiting_interface').fadeIn(400);

	var conn = null;
	conn = new SockJS('https://' + window.location.host + '/router', 'websocket');

	conn.onopen = function() {
		conn.send('Open:' + $('#username').text());
	};

	var my_turn = false;
	var first_turn = true;

	conn.onmessage = function(e) {
		var command = e.data.split(':')[0];
		var info    = e.data.split(':')[1];

		switch(command) {
			case 'Names':
				var player_count = info.split(',').length;
				var player_names = info.split(',').join('<br>');
				$('#connections').html(player_names);
				if (player_count >=2)
					$('#play_button').fadeIn(400);
				else
					$('#play_button').fadeOut(400);
				break;

			case 'Start':
				$('#waiting_interface').fadeOut(400);
				$('#game_interface').show();
				$('#end_game_form').hide();
				$('#decision_form').hide();
				$('#play_all_button').off('click')
				$('#end_button').off('click');
				$('#play_all_button').on('click', play_all_handler)
				$('#end_button').on('click', end_handler);
				break;

			case 'Supply':
				$('.supply_row').html('');
				var supply = info.split(',');
				for (var i = 0; i < supply.length; i++) {
					if (i % 2 == 0) {
						if (i < 16)
							$('.supply_row').eq(0).append('<figure></figure>');
						else
							$('.supply_row').eq(1).append('<figure></figure>');
						$(new Image()).attr('src', '/static/images/' + supply[i] + '.jpg').height('calc(100% - 20px)').appendTo($('.supply_row > figure:last'));
					}
					else {
						$('.supply_row > figure:last').append('<figcaption>' + supply[i] + '</figcaption>');
					}
				}

				$('.supply_row img').on('click', function() {
					if (my_turn == true) {
						conn.send($('#username').text() + ':Buy Card:' + $('.supply_row img').index($(this)));
					}
				});
				break;

			case 'Curses':
				$('#curses > figure').html('');
				$(new Image()).attr('src', '/static/images/' + info.split(',')[0] + '.jpg').height('calc(100% - 20px)').appendTo($('#curses > figure'));
				$('#curses > figure').append('<figcaption>' + info.split(',')[1] + '</figcaption>');

				$('#curses img').off('click');
				$('#curses img').on('click', function() {
					if (my_turn == true) {
						conn.send($('#username').text() + ':Buy Card:16');
					}
				});
				break;

			case 'Trash':
				$('#trash > figure').html('');
				$(new Image()).attr('src', '/static/images/' + info.split(',')[0] + '.jpg').height('calc(100% - 20px)').appendTo($('#trash > figure'));
				$('#trash > figure').append('<figcaption>' + info.split(',')[1] + '</figcaption>');

				$('#trash img').off('click');
				$('#trash img').on('click', function() {
					conn.send('Trash:');
				});
				break;

			case 'Hand':
				$('#hand').html('');
				if (info != '(blank)') {
					var hand = info.split(',');
					
					for (var i = 0; i < hand.length; i++) {
						$(new Image()).attr('src', '/static/images/' + hand[i] + '.jpg').height('100%').appendTo($('#hand'));
					}

					$('#hand > img').on('click', function() {
						if (my_turn == true) {
							conn.send($('#username').text() + ':Play Card:' + $('#hand > img').index($(this)));
						}
					});
				}
				break;

			case 'Turn':
				if ($('#username').text() == info) {
					my_turn = true;
				}
				else {
					$('#stats').html('Actions: <br>Gold: <br>Buys: ');
					my_turn = false;
				}
				if (first_turn == false) {
					span = '<span></span>';
					$('#log').html($('#log').html() + '<br>' + span + '<br>');
					$('#log > span:last').text('-- ' + info + "'s turn --");
					$('#log').scrollTop($('#log')[0].scrollHeight);
				}
				else {
					span = '<span></span>';
					$('#log').html($('#log').html()  + span + '<br>');
					$('#log > span:last').text('-- ' + info + "'s turn --");
					$('#log').scrollTop($('#log')[0].scrollHeight);
					first_turn = false;
				}
				break;

			case 'Stats':
				if (my_turn == true) {
					var actions = info.split(',')[0];
					var gold    = info.split(',')[1];
					var buys    = info.split(',')[2];
					$('#stats').html('Actions: ' + actions + '<br>' + 'Gold: ' + gold + '<br>' + 'Buys: ' + buys);
				}
				break;

			case 'Deck':
				$('#deck > figure').html('');
				$(new Image()).attr('src', '/static/images/' + info.split(',')[0] + '.jpg').height('calc(100% - 20px)').appendTo($('#deck > figure'));
				$('#deck > figure').append('<figcaption>' + info.split(',')[1] + '</figcaption>');
				break;

			case 'Discard':
				$('#discard > figure').html('');
				$(new Image()).attr('src', '/static/images/' + info.split(',')[0] + '.jpg').height('calc(100% - 20px)').appendTo($('#discard > figure'));
				$('#discard > figure').append('<figcaption>' + info.split(',')[1] + '</figcaption>');
				break;

			case 'Chat':
				var msg = e.data.slice(e.data.indexOf(':') + 1);
				$('#log').html($('#log').html() + '<span class="chat"></span><br>');
				$('#log > span:last').text(msg);
				$('#log').scrollTop($('#log')[0].scrollHeight);
				break;

			case 'End Game':
				$('#hand > img').off('click');
				$('#supply_box img').off('click');
				$('#curses img').off('click');
				$('#trash img').off('click');
				$('#play_all_button').off('click');
				$('#end_button').off('click');

				var msg = e.data.split(':')[1];
				$('#end_game_form span').html(msg);
				$('#end_game_form').fadeIn(400);

				$('#end_game_form input').eq(0).on('click', function(e) {
					e.preventDefault();
					$('#end_game_form > form').attr('method', 'post');
					$('#end_game_form > form').attr('action', '/');
					$('#end_game_form input').eq(2).val($('#username').text());
					conn.close();
					$('#end_game_form > form').submit();
				});

				$('#end_game_form input').eq(1).on('click', function(e) {
					e.preventDefault();
					$('#end_game_form > form').attr('method', 'get');
					$('#end_game_form > form').attr('action', '/');
					$('#end_game_form input').eq(2).remove();
					conn.close();
					$('#end_game_form > form').submit();
				});
				break;

			case 'Leave':
				$('#hand > img').off('click');
				$('#supply_box img').off('click');
				$('#curses img').off('click');
				$('#trash img').off('click');
				$('#play_all_button').off('click');
				$('#end_button').off('click');

				var msg = e.data.split(':')[1];
				$('#log').html($('#log').html() + '<span class="error"></span><br>');
				$('#log > span:last').text(msg);
				$('#log').scrollTop($('#log')[0].scrollHeight);

				$('#end_game_form span').html(msg);
				$('#end_game_form').fadeIn(400);

				$('#end_game_form input').eq(0).on('click', function(e) {
					e.preventDefault();
					$('#end_game_form > form').attr('method', 'post');
					$('#end_game_form > form').attr('action', '/');
					$('#end_game_form input').eq(2).val($('#username').text());
					conn.close();
					$('#end_game_form > form').submit();
				});

				$('#end_game_box input').eq(1).on('click', function(e) {
					e.preventDefault();
					$('#end_game_form > form').attr('method', 'get');
					$('#end_game_form > form').attr('action', '/');
					$('#end_game_form input').eq(2).remove();
					conn.close();
					$('#end_game_form > form').submit();
				});
				break;

			case 'Public':
				var public_msg = e.data.split(':')[1];
				$('#log').html($('#log').html() + '<span></span><br>');
				$('#log > span:last').text(public_msg);
				$('#log').scrollTop($('#log')[0].scrollHeight);
				break;

			case 'Private':
				var name = e.data.split(':')[1];
				var cmd  = e.data.split(':')[2];

				if (name == $('#username').text()) {
					switch(cmd) {
						case 'Select':
							$('#hand > img').off('click');
							$('#supply_box img').off('click');
							$('#curses img').off('click');
							$('#play_all_button').off('click');
							$('#end_button').off('click');

							var msg = e.data.split(':')[3];
							if (msg != '(blank)') {
								$('#log').html($('#log').html() + '<span></span><br>');
								$('#log > span:last').text(msg);
								$('#log').scrollTop($('#log')[0].scrollHeight);
							}

							$('#hand > img').on('click', function() {
								if ($(this).hasClass('img_selected'))
									$(this).removeClass('img_selected');
								else
									$(this).addClass('img_selected');
							});

							$('#done_button').fadeIn(400);
							$('#done_button').on('click', function() {
								var resp = '';
								for (var i = 0; i < $('#hand > img').length; i++) {
									if ($('#hand > img').eq(i).hasClass('img_selected')) {
										if (resp == '')
											resp = i.toString();
										else
											resp = resp + ' ' + i.toString();
									}
								}
								conn.send($('#username').text() + ':Play Card:' + resp);
								$('#done_button').fadeOut(400);
								$('#done_button').off('click');
								$('#play_all_button').on('click', play_all_handler)
								$('#end_button').on('click', end_handler);
							});
							break;

						case 'Decision':
							$('#hand > img').off('click');
							$('#supply_box img').off('click');
							$('#curses img').off('click');
							$('#play_all_button').off('click');
							$('#end_button').off('click');

							var opt_string = e.data.split(':')[3];
							var opt1 = e.data.split(':')[4];
							var opt2 = e.data.split(':')[5];
							$('#decision_form span').text(opt_string);
							$('#decision_form input').eq(0).attr('value', opt1);
							$('#decision_form input').eq(1).attr('value', opt2);

							$('#decision_form').fadeIn(400);
							$('#decision_form input').on('click', function(e) {
								e.preventDefault();
								conn.send($('#username').text() + ':Play Card:' + $('#decision_form input').index($(this)));
								$('#decision_form input').off('click');
								$('#decision_form').fadeOut(400);
								$('#play_all_button').on('click', play_all_handler)
								$('#end_button').on('click', end_handler);
							});
							break;

						case 'Gain':
							$('#hand > img').off('click');
							$('#supply_box img').off('click');
							$('#curses img').off('click');
							$('#play_all_button').off('click');
							$('#end_button').off('click');

							var msg = e.data.split(':')[3];
							if (msg != '(blank)') {
								$('#log').html($('#log').html() + '<span></span><br>');
								$('#log > span:last').text(msg);
								$('#log').scrollTop($('#log')[0].scrollHeight);
							}

							$('#supply_box img').on('click', function() {
								conn.send($('#username').text() + ':Play Card:' + $('#supply_box img').index($(this)));
								$('#supply_box img').off('click');
								$('#play_all_button').on('click', play_all_handler)
								$('#end_button').on('click', end_handler);
							});
							break;

						case 'Discard':
							$('#hand > img').off('click');
							$('#supply_box img').off('click');
							$('#curses img').off('click');
							$('#play_all_button').off('click');
							$('#end_button').off('click');

							var msg = e.data.split(':')[3];
							if (msg != '(blank)') {
								$('#log').html($('#log').html() + '<span></span><br>');
								$('#log > span:last').text(msg);
								$('#log').scrollTop($('#log')[0].scrollHeight);
							}

							$('#hand > img').on('click', function() {
								if ($(this).hasClass('img_selected'))
									$(this).removeClass('img_selected');
								else
									$(this).addClass('img_selected');
							});

							$('#done_button').fadeIn(400);
							$('#done_button').on('click', function() {
								var resp = '';
								for (var i = 0; i < $('#hand > img').length; i++) {
									if ($('#hand > img').eq(i).hasClass('img_selected')) {
										if (resp == '')
											resp = i.toString();
										else
											resp = resp + ' ' + i.toString();
									}
								}
								conn.send($('#username').text() + ':Play Card:' + resp);
								$('#done_button').off('click');
								$('#done_button').fadeOut(400);
								$('#play_all_button').on('click', play_all_handler)
								$('#end_button').on('click', end_handler);
							});
							break;

						case 'Suspend':
							$('#hand > img').off('click');
							$('#supply_box img').off('click');
							$('#curses img').off('click');
							$('#play_all_button').off('click');
							$('#end_button').off('click');

							var msg = e.data.split(':')[3];
							if (msg != '(blank)') {
								$('#log').html($('#log').html() + '<span></span><br>');
								$('#log > span:last').text(msg);
								$('#log').scrollTop($('#log')[0].scrollHeight);
							}
							break;

						case 'Resume':
							$('#play_all_button').off('click');
							$('#end_button').off('click');
							$('#play_all_button').on('click', play_all_handler)
							$('#end_button').on('click', end_handler);
							break;

						case 'Error':
							var msg = e.data.split(':')[3];
							$('#log').html($('#log').html() + '<span class="error"></span><br>');
							$('#log > span:last').text(msg);
							$('#log').scrollTop($('#log')[0].scrollHeight);
							break;

						default:
							console.log('Received invalid command.');
							break;
					}
				}
			default:
				console.log('Received invalid command.');
				break;
		}
	};

	function play_all_handler() {
		if (my_turn)
			conn.send($('#username').text() + ':Play All Treasures');
	}

	$('#play_all_button').on('click', play_all_handler)

	function end_handler() {
		if (my_turn)
			conn.send($('#username').text() + ':End Turn');
	}

	$('#end_button').on('click', end_handler);

	$('#chat_box > form').submit(function(e) {
		e.preventDefault();
		if ($('#chat_box input').val() != '') {
			conn.send('Chat:' + '(' + $('#username').text() + ') ' + $('#chat_box input').val());
			$('#chat_box input').val('');
		}
	});

	$('#waiting_interface > form').submit(function(e) {
		e.preventDefault();
		$('#waiting_interface').fadeOut(400, function() {
			conn.send('Start: (blank)');
		});
	});
});
