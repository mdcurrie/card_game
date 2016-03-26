import os.path
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import sockjs.tornado
import dominion

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html', error='')

	def post(self):
		name = self.get_argument('name')

		if GameConnection.game != None:
			self.render('index.html', error='A match is already in progress, please try again later.')
		elif len(GameConnection.participants) >= 4:
			self.render('index.html', error='We are at maximum player count, please try again later.')
		elif name in GameConnection.names:
			self.render('index.html', error='That name is already taken, please try again.')
		else:
			self.render('dominion.html', name=name)

class GameConnection(sockjs.tornado.SockJSConnection):
	participants = []
	names = []
	game = None
	coro = None

	def on_open(self, info):
		cls = GameConnection
		cls.participants.append(self)

	def on_message(self, message):
		cls     = GameConnection
		command = message.split(':')[0]
		info    = message.split(':')[1]

		if command == 'Open':
			cls.names.append(info)
			self.broadcast(cls.participants, 'Names:' + ','.join(name for name in cls.names))

		elif command == 'Chat':
		 	self.broadcast(cls.participants, message)

		elif command == 'Trash':
			cls = GameConnection
			if cls.game._trash.is_empty():
				self.send('Public:The trash is empty.')
			else:
				self.send('Public:Cards in trash are ' + ', '.join([card.name for card in cls.game._trash]) + '.')

		elif command == 'Start':
			self.broadcast(cls.participants, 'Start: (blank)')
			cls.game = dominion.Dominion(cls.names)
			cls.coro = cls.game.game_loop()
			ret = next(cls.coro)
			self.broadcast(cls.participants, ret)
			self.display_supply()
			self.display_curses()
			self.display_trash()
			self.display_hands()
			self.display_stats()
			self.display_decks()
			self.display_discards()

		else:
			ret = cls.coro.send(message)
			self.display_supply()
			self.display_curses()
			self.display_trash()
			self.display_hands()
			while cls.game.info_list != []:
				msg = cls.game.info_list.pop(0)
				self.broadcast(cls.participants, msg)
				if msg.split(':')[0] == 'End Game':
					cls.game = None
					return
			if ret: self.broadcast(cls.participants, ret)
			self.display_stats()
			self.display_decks()
			self.display_discards()

	def on_close(self):
		cls = GameConnection
		idx = cls.participants.index(self)
		cls.participants.pop(idx)
		rage_quitter = cls.names.pop(idx)
		self.broadcast(cls.participants, 'Names:' + ','.join(name for name in cls.names))
		if cls.participants == []:
			cls.game = None
		self.broadcast(cls.participants, 'Leave:{} has left the game.'.format(rage_quitter))

	def display_supply(self):
		cls = GameConnection
		self.broadcast(cls.participants, 'Supply:' + cls.game.supply_string())

	def display_curses(self):
		cls = GameConnection
		self.broadcast(cls.participants, 'Curses:' + cls.game.curse_string())

	def display_trash(self):
		cls = GameConnection
		self.broadcast(cls.participants, 'Trash:' + cls.game.trash_string())

	def display_hands(self):
		cls = GameConnection
		for idx, participant in enumerate(cls.participants):
			participant.send('Hand:' + cls.game.hand_string(idx))

	def display_discards(self):
		cls = GameConnection
		for idx, participant in enumerate(cls.participants):
			participant.send('Discard:' + cls.game.discard_string(idx))

	def display_stats(self):
		cls = GameConnection
		for idx, participant in enumerate(cls.participants):
			participant.send('Stats:' + cls.game.stats_string(idx))

	def display_decks(self):
		cls = GameConnection
		for idx, participant in enumerate(cls.participants):
			participant.send('Deck:' + cls.game.deck_string(idx))

if __name__ == '__main__':
	GameRouter = sockjs.tornado.SockJSRouter(GameConnection, '/router')

	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[(r'/', IndexHandler)] + GameRouter.urls,
				  template_path=os.path.join(os.path.dirname(__file__), 'templates'),
				  static_path=os.path.join(os.path.dirname(__file__), 'static'),
				  debug=True
		)

	app.listen(int(os.environ.get('PORT', 8000)))
	tornado.ioloop.IOLoop.instance().start()

	#KNOWN BUGS:
	# 1. clean up HTML/CSS/JS (maybe?)
	
