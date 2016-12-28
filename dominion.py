import cards
import player
from copy import copy
from random import shuffle
from itertools import cycle

class Dominion:
	"""A class to represent the game of Dominion. 2 to 4 players.
	   Manages the supply piles and player turns."""

	def __init__(self, player_names=None):
		# initializes the decks and supply piles
		self.info_list = []
		self.resolved  = True
		self.coro      = None

		player_count = len(player_names)
		assert player_count in {2, 3, 4}

		self._players = []
		for p in player_names:
			self._players.append(player.Player(p))

		# initialize the treasure, victory, and kingdom cards
		self.init_treasure_cards(player_count)
		self.init_victory_cards(player_count)
		self.init_kingdom_cards()

		# the trash pile is empty
		self._trash = cards.Cards()

		# 10 curses for a 2 player game, 20 for 3 players, 30 for 4 players
		self._curses = cards.Cards()
		curse_amount = {2: 10, 3: 20, 4: 30}
		for amount in range(curse_amount[player_count]):
			self._curses.add_cards(cards.Card('Curse', 'Curse', 0))
			
		self.info_list.append("-- Starting game between " + ', '.join([self._players]) + " --")

	def __getitem__(self, index):
		# allows indexing to be performed on the class
		try:
			return self._players[index]
		except IndexError:
			sys.stderr.write('IndexError in Dominion.__getitem__()\n')

	def __len__(self):
		# returns the total number of supply piles that are not empty
		total = 0
		for supply in [self._treasures, self._victories, self._kingdoms]:
			for piles in supply:
				if piles.is_empty() == False:
					total += 1
		if self._curses.is_empty() == False:
			total += 1

		return total

	def init_treasure_cards(self, player_count):
		# initializes the treasure cards
		self._treasures = []

		# 46 coppers for a 2 player game, 39 for 3 players, 32 for 4 players
		coppers = cards.Cards()
		copper_amount = {2: 46, 3: 39, 4: 32}
		for amount in range(copper_amount[player_count]):
			coppers.add_cards(cards.Card('Copper', 'Treasure', 0))

		# 40 silvers
		silvers = cards.Cards()
		for amount in range(40):
			silvers.add_cards(cards.Card('Silver', 'Treasure', 3))

		# 30 golds
		golds = cards.Cards()
		for amount in range(30):
			golds.add_cards(cards.Card('Gold', 'Treasure', 6))

		self._treasures.extend([coppers, silvers, golds])

	def init_victory_cards(self, player_count):
		# initializes the victory cards
		self._victories = []

		# 8 of each victory card for a 2 player game, 12 for 3 or 4 players
		estates   = cards.Cards()
		duchies   = cards.Cards()
		provinces = cards.Cards()
		victory_amount = {2: 8, 3: 12, 4: 12}
		for amount in range(victory_amount[player_count]):
			estates.add_cards(cards.Card('Estate', 'Victory', 2))
			duchies.add_cards(cards.Card('Duchy', 'Victory', 5))
			provinces.add_cards(cards.Card('Province', 'Victory', 8))

		self._victories.extend([estates, duchies, provinces])

	def init_kingdom_cards(self):
		# the kingdom cards has 10 supply piles.
		# each supply pile has 10 of the same card from the randomizers list
		self._kingdoms = []
		randomizers = [
			cards.Card('Cellar', 		'Action', 	2),
			cards.Card('Chapel', 		'Action', 	2),
			cards.Card('Moat', 			'Action', 	2),
			cards.Card('Chancellor', 	'Action', 	3),
			cards.Card('Village', 		'Action',	3),
			cards.Card('Woodcutter', 	'Action',	3),
			cards.Card('Workshop', 		'Action', 	3),
			cards.Card('Bureaucrat', 	'Action', 	4),
			cards.Card('Feast', 		'Action', 	4),
			cards.Card('Gardens', 		'Victory', 	4),
			cards.Card('Militia', 		'Action', 	4),
			cards.Card('Moneylender', 	'Action', 	4),
			cards.Card('Remodel', 		'Action', 	4),
			cards.Card('Smithy', 		'Action', 	4),
			cards.Card('Spy', 			'Action', 	4),
			cards.Card('Thief', 		'Action', 	4),
			cards.Card('Throne Room', 	'Action', 	4),
			cards.Card('Council Room', 	'Action', 	5),
			cards.Card('Festival', 		'Action', 	5),
			cards.Card('Laboratory', 	'Action', 	5),
			cards.Card('Library', 		'Action', 	5),
			cards.Card('Market', 		'Action', 	5),
			cards.Card('Mine', 			'Action', 	5),
			cards.Card('Witch', 		'Action', 	5),
			cards.Card('Adventurer', 	'Action', 	6),
			]

		# randomly select 10 cards to be the kingdom cards of the supply pile
		shuffle(randomizers)
		for pile_num in range(10):
			pile = cards.Cards()
			if randomizers[pile_num].name == 'Gardens':
				if len(self._players) == 2:
					card_copies = [copy(randomizers[pile_num]) for amount in range(8)]
				else:
					card_copies = [copy(randomizers[pile_num]) for amount in range(12)]
			else:
				card_copies = [copy(randomizers[pile_num]) for amount in range(10)]
			pile.add_cards(card_copies)
			self._kingdoms.append(pile)

	def game_loop(self):
		# the main loop of the game, cycles through all players until game is over
		# each player chooses to play a card from hand or several other options
		for current_player in cycle(self._players):
			current_player.actions = 1
			current_player.buys    = 1
			current_player.gold    = 0
			first_move = True	
			while current_player.buys > 0:
				if first_move == True:
					user_input = yield 'Turn:{}'.format(current_player.name)
					first_move = False
				else:
					user_input = yield
				info = user_input.split(':', 1)
				info = info[1].split(':')
				if info[0] == 'Play All Treasures':
					self.play_all_treasures(current_player)
				elif info[0] == 'End Turn':
					break
				elif info[0] == 'Play Card':
					if self.resolved == True:
						idx = int(info[1])
						self.play_card(current_player, idx)
					else:
						try:
							self.coro.send(info[1])
						except StopIteration:
							self.resolved = True
				elif info[0] == 'Buy Card':
					idx = int(info[1])
					self.buy_card(current_player, idx)

			current_player.end_turn()
			# end the game if all provinces or 3 supply piles are empty
			if self._victories[2].is_empty() or len(self) <= 14:
				self.end_game()

	def play_card(self, current_player, idx):
		# play a card from hand
		if current_player[('hand', idx)].type == 'Action':
			if current_player.actions == 0:
				self.info_list.append('Private:{}:Error:You have no more actions, try again!'.format(current_player.name))
				return

		if current_player[('hand', idx)].type == 'Victory':
			self.info_list.append('Private:{}:Error:You cannot play a victory card, try again!'.format(current_player.name))
			return

		if current_player[('hand', idx)].type == 'Curse':
			self.info_list.append('Private:{}:Error:You cannot play a Curse, try again!'.format(current_player.name))
			return

		card_to_play = current_player.remove_card('hand', idx)
		current_player.add_cards('in play', card_to_play)

		if current_player[('in play', -1)].type == 'Treasure':
			self.play_treasure(current_player)
		elif current_player[('in play', -1)].type == 'Action':
			current_player.actions -= 1
			self.coro = self.play_action(current_player)
			try:
				next(self.coro)
			except StopIteration:
				self.resolved = True
			else:
				self.resolved = False

	def play_treasure(self, current_player):
		# play a treasure from hand to increase gold count
		# playing a treasure ends the player's action phase
		current_player.actions = 0
		if current_player[('in play', -1)].name == 'Copper':
			current_player.gold += 1
		elif current_player[('in play', -1)].name == 'Silver':
			current_player.gold += 2
		elif current_player[('in play', -1)].name == 'Gold':
			current_player.gold += 3

		self.info_list.append('Public:{} played a {}.'.format(current_player.name, current_player[('in play', -1)].name))

	def play_all_treasures(self, current_player):
		# play all treasures from hand to increase gold count
		idx = 0
		while idx < current_player.length('hand'):
			if current_player[('hand', idx)].name in {'Copper', 'Silver', 'Gold'}:
				self.play_card(current_player, idx)
			else:
				idx += 1

	def buy_card(self, current_player, idx):
		# allows players to buy cards from the supply piles
		if current_player.buys <= 0:
			self.info_list.append('Private:{}:Error:You have no more buys.'.format(current_player.name))

		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)
		supply.append(self._curses)

		if supply[idx].is_empty() == False:
			if supply[idx][-1].cost <= current_player.gold:
				card_to_buy = supply[idx].remove_card()
				current_player.gold -= card_to_buy.cost
				current_player.buys -= 1
				current_player.actions = 0
				current_player.add_cards('discard', card_to_buy)
				self.info_list.append('Public:{} bought a {}.'.format(current_player.name, card_to_buy.name))
			else:
				self.info_list.append('Private:{}:Error:You cannot afford that card, try again!'.format(current_player.name))
		else:
			self.info_list.append('Private:{}:Error:The supply pile for that card is empty, try again!'.format(current_player.name))

	def play_action(self, current_player):
		# play an action card from hand
		other_players = set(self._players) - set([current_player])
		played_card = current_player[('in play', -1)]
		moat = cards.Card('Moat', 'Action', 2)
		
		self.info_list.append('Public:{} played a {}.'.format(current_player.name, played_card.name))

		if played_card.name == 'Cellar':
			current_player.actions += 1
			if current_player.is_empty('hand'):
				self.info_list.append('Public:{} has no cards to discard.'.format(current_player.name))
				return

			self.info_list.append('Private:{}:Select:Choose any number of cards to discard.'.format(current_player.name))
			discard_list = yield
			discard_list = discard_list[::-1]
			discard_list = discard_list.split(' ')
			self.info_list.append('Public:{} discarded '.format(current_player.name))
			if discard_list == ['']:
				self.info_list[-1] += 'no cards.'
				return
			for idx in discard_list:
				discarded_card = current_player.remove_card('hand', int(idx))
				if idx == discard_list[-1]:
					self.info_list[-1] += discarded_card.name + '.'
				else:
					self.info_list[-1] += discarded_card.name + ', '
				current_player.add_cards('discard', discarded_card)

			for idx in discard_list:
				current_player.draw_card()
			self.info_list.append('Public:{} drew {} cards.'.format(current_player.name, len(discard_list)))

		elif played_card.name == 'Chapel':
			if current_player.is_empty('hand'):
				self.info_list.append('Public:{} has no cards to trash.'.format(current_player.name))
				return

			self.info_list.append('Private:{}:Select:Choose up to 4 cards to trash.'.format(current_player.name))
			trash_list = yield
			trash_list = trash_list[::-1]
			trash_list = trash_list.split(' ')[:4]
			self.info_list.append('Public:{} trashed '.format(current_player.name))
			if trash_list == ['']:
				self.info_list[-1] += 'no cards.'
				return
			for idx in trash_list:
				trashed_card = current_player.remove_card('hand', int(idx))
				if idx == trash_list[-1]:
					self.info_list[-1] += trashed_card.name + '.'
				else:
					self.info_list[-1] += trashed_card.name + ', '
				self._trash.add_cards(trashed_card)

		elif played_card.name == 'Moat':
			for amount in range(2): current_player.draw_card()

		elif played_card.name == 'Chancellor':
			current_player.gold += 2
			self.info_list.append('Private:{}:Decision:Place deck into discard pile?:Yes:No'.format(current_player.name))
			user_input = yield
			if user_input == '0':
				current_player.transfer_cards('deck', 'discard')
				self.info_list.append('Public:{} placed deck into discard pile.'.format(current_player.name))
			else:
				self.info_list.append('Public:{} did not place deck into discard pile.'.format(current_player.name))

		elif played_card.name == 'Village':
			current_player.draw_card()
			current_player.actions += 2

		elif played_card.name == 'Woodcutter':
			current_player.buys += 1
			current_player.gold += 2

		elif played_card.name == 'Workshop':
			self.info_list.append('Private:{}:Gain:Gain a card costing up to 4.'.format(current_player.name))
			while True:
				idx = yield
				if self.gain_card(current_player, 4, int(idx), {'Treasure', 'Victory', 'Action'}): break
				self.info_list.append('Private:{}:Gain:(blank)'.format(current_player.name))

		elif played_card.name == 'Bureaucrat':
			if self._treasures[1].is_empty() == False:
				gained_silver = self._treasures[1].remove_card()
				current_player.add_cards('deck', gained_silver)
				self.info_list.append('Public:{} gained a Silver.'.format(current_player.name))
			else:
				self.info_list.append('Public:There are no more Silvers.')
			
			for others in other_players:
				if moat in others:
					self.info_list.append('Public:{} blocked the attack using Moat.'.format(others.name))
					continue
				for idx, card in enumerate(others):
					if card.name in {'Estate', 'Duchy', 'Province', 'Gardens'}:
						removed_victory = others.remove_card('hand', idx)
						others.add_cards('deck', removed_victory)
						self.info_list.append('Public:{} placed {} on top of his deck.'.format(others.name, card.name))
						break
				else:
					card_list = [card.name for card in others]
					card_string = 'Public:{} revealed '.format(others.name) + ', '.join(card_list) + '.'
					self.info_list.append(card_string)

		elif played_card.name == 'Feast':
			feast = current_player.remove_card('in play')
			self._trash.add_cards(feast)
			self.info_list.append('Private:{}:Gain:Gain a card costing up to 5.'.format(current_player.name))
			while True:
				idx = yield
				if self.gain_card(current_player, 5, int(idx), {'Treasure', 'Victory', 'Action'}): break
				self.info_list.append('Private:{}:Gain:(blank)'.format(current_player.name))

		elif played_card.name == 'Militia':
			current_player.gold += 2
			for others in other_players:
				if others.length('hand') <= 3:
					self.info_list.append('Public:{} has 3 or fewer cards in hand.'.format(others.name))
					continue
				if moat in others:
					self.info_list.append('Public:{} blocked the attack using Moat.'.format(others.name))
					continue

				self.info_list.append('Private:{}:Suspend:Waiting for {} to discard...'.format(current_player.name, others.name))
				self.info_list.append('Private:{}:Discard:Discard down to 3 cards.'.format(others.name))
				card_names = 'Public:{} discarded '.format(others.name)
				while True:
					discard_list = yield
					discard_list = discard_list[::-1]
					discard_list = discard_list.split(' ')
					if discard_list == ['']:
						self.info_list.append('Private:{}:Error:You must select cards to discard, try again!'.format(others.name))
						self.info_list.append('Private:{}:Suspend:(blank)'.format(current_player.name, others.name))
						self.info_list.append('Private:{}:Discard:(blank)'.format(others.name))
						continue
					elif others.length('hand') - len(discard_list) == 3:
						for idx in discard_list:
							discarded_card = others.remove_card('hand', int(idx))
							if idx == discard_list[-1]:
								card_names += discarded_card.name + '.'
							else:
								card_names += discarded_card.name + ', '
							others.add_cards('discard', discarded_card)
						self.info_list.append(card_names)
						break
					else:
						self.info_list.append('Private:{}:Error:You must discard down to 3, try again!'.format(others.name))
						self.info_list.append('Private:{}:Suspend:(blank)'.format(current_player.name, others.name))
						self.info_list.append('Private:{}:Discard:(blank)'.format(others.name))
			self.info_list.append('Private:{}:Resume:(blank)'.format(current_player.name))

		elif played_card.name == 'Moneylender':
			for idx, card in enumerate(current_player):
				if card.name == 'Copper':
					trashed_copper = current_player.remove_card('hand', idx)
					self.info_list.append('Public:{} trashed a Copper.'.format(current_player.name))
					self._trash.add_cards(trashed_copper)
					current_player.gold += 3
					return
			else:
				self.info_list.append('Public:{} does not have a Copper to trash.'.format(current_player.name))

		elif played_card.name == 'Remodel':
			if current_player.is_empty('hand'):
				self.info_list.append("Public:{}'s hand is empty.".format(current_player.name))
				return

			self.info_list.append('Private:{}:Select:Choose a card to trash.'.format(current_player.name))
			while True:
				idx = yield
				if idx != '':
					break
				self.info_list.append('Private:{}:Error:You must select a card to trash, try again!'.format(current_player.name))
				self.info_list.append('Private:{}:Select:(blank)'.format(current_player.name))

			idx = int(idx.split(' ')[0])
			trashed_card = current_player.remove_card('hand', idx)
			self._trash.add_cards(trashed_card)	
			self.info_list.append('Public:{} trashed a {}.'.format(current_player.name, trashed_card.name))
			self.info_list.append('Private:{}:Gain:Gain a card costing up to {}.'.format(current_player.name, trashed_card.cost + 2))		
			while True:
				idx = yield
				if self.gain_card(current_player, trashed_card.cost + 2, int(idx), {'Treasure', 'Victory', 'Action'}): break
				self.info_list.append('Private:{}:Gain:(blank)'.format(current_player.name))

		elif played_card.name == 'Smithy':
			for amount in range(3): current_player.draw_card()

		elif played_card.name == 'Spy':
			current_player.draw_card()
			current_player.actions += 1
			for p in self._players:
				if p in other_players:
					if moat in p:
						self.info_list.append('Public:{} blocked the attack using Moat.'.format(p.name))
						continue
				if p.is_empty('deck'):
					if p.is_empty('discard'):
						print('Public:{} cannot reveal a card.'.format(p.name))
						continue
					p.transfer_cards('discard', 'deck')
					p.shuffle()
				revealed_card = p[('deck', -1)]
				self.info_list.append('Public:{} revealed a {}.'.format(p.name, revealed_card.name))
				if p in other_players:
					self.info_list.append('Private:{}:Decision:Make {} discard the revealed {}?:Yes:No'.format(current_player.name, p.name, revealed_card.name))
				else:
					self.info_list.append('Private:{}:Decision:Discard the revealed {}?:Yes:No'.format(current_player.name, revealed_card.name))
				user_input = yield
				if user_input == '0':
					revealed_card = p.remove_card('deck')
					p.add_cards('discard', revealed_card)
					self.info_list.append('Public:{} discarded the {}.'.format(p.name, revealed_card.name))
				else:
					self.info_list.append('Public:{} did not discard the {}.'.format(p.name, revealed_card.name))

		elif played_card.name == 'Thief':
			for others in other_players:
				trashed = False
				if moat in others:
					self.info_list.append('Public:{} blocked the attack using Moat.'.format(others.name))
					continue
				revealed_cards = []
				for amount in range(2):
					if others.is_empty('deck'):
						if others.is_empty('discard'): break
						others.transfer_cards('discard', 'deck')
						others.shuffle()
					revealed_cards.append(others.remove_card('deck'))

				if revealed_cards == []:
					self.info_list.append('Public:{} could not reveal any cards.'.format(others.name))
					continue

				card_names = [card.name for card in revealed_cards]
				self.info_list.append('Public:{} revealed '.format(others.name) + ', '.join(card_names) + '.')
				for card in card_names:
					if card in {'Copper', 'Silver', 'Gold'}: break
				else:
					self.info_list.append('Public:{} had no treasures to reveal.'.format(others.name))
					others.add_cards('discard', revealed_cards)
					self.info_list.append('Public:{} discarded '.format(others.name) + ', '.join(card_names) + '.')
					continue
				
				treasure_count = card_names.count('Copper') + card_names.count('Silver') + card_names.count('Gold')
				if treasure_count == 1:
					if card_names[0] in {'Copper', 'Silver', 'Gold'}:
						idx = 0
					else:
						idx = 1
					trashed_card = revealed_cards.pop(idx)
					self._trash.add_cards(trashed_card)
					trashed = True
					self.info_list.append('Public:{} trashed the revealed {}.'.format(others.name, card_names[idx]))
				else:
					self.info_list.append('Private:{}:Decision:Make {} trash the {} or {}?:{}:{}'.format(current_player.name, others.name,
																								card_names[0], card_names[1], 
																							  	card_names[0], card_names[1]))
					user_input = yield
					if user_input == '0':
						trashed_card = revealed_cards.pop(0)
					else:               
						trashed_card = revealed_cards.pop(1)

					self._trash.add_cards(trashed_card)
					trashed = True
					self.info_list.append('Public:{} trashed the revealed {}.'.format(others.name, trashed_card.name))

				if revealed_cards != []:
					self.info_list.append('Public:{} discarded the revealed {}.'.format(others.name, revealed_cards[0].name))
					others.add_cards('discard', revealed_cards)

				if trashed == True:
					self.info_list.append('Private:{}:Decision:Gain the trashed {}?:Yes:No'.format(current_player.name, trashed_card.name))
					user_input = yield
					if user_input == '0':
						gained_card = self._trash.remove_card()
						current_player.add_cards('discard', gained_card)
						self.info_list.append('Public:{} gained the trashed {}.'.format(current_player.name, gained_card.name))
					else:
						self.info_list.append('Public:{} did not gain the trashed {}.'.format(current_player.name, trashed_card.name))

		elif played_card.name == 'Throne Room':
			if current_player.is_empty('hand'):
				self.info_list.append('Public:{} has no cards in hand.'.format(current_player.name))
				return
			for card in current_player:
				if card.type == 'Action': break
			else:
				self.info_list.append('Public:{} has no actions to choose from.'.format(current_player.name))
				return

			self.info_list.append('Private:{}:Select:Choose an action card.'.format(current_player.name))
			while True:
				idx = yield
				if idx == '':
					self.info_list.append('Private:{}:Error:You must select a card from your hand, try again!'.format(current_player.name))
				else:
					idx = int(idx.split(' ')[0])
					if current_player[('hand', idx)].type == 'Action':
						break
					else:
						self.info_list.append('Private:{}:Error:You must select an action card, try again!'.format(current_player.name))
				self.info_list.append('Private:{}:Select:(blank)'.format(current_player.name))

			# feast and throne room are special cases
			if current_player[('hand', idx)].name == 'Feast':
				card_to_play = current_player.remove_card('hand', idx)
				current_player.add_cards('in play', card_to_play)
				coro = self.play_action(current_player)
				try:
					next(coro)
				except StopIteration:
					pass
				else:
					while True:
						info = yield
						try:
							coro.send(info)
						except StopIteration:
							break

				card_to_play = self._trash.remove_card()
				current_player.add_cards('in play', card_to_play)
				coro = self.play_action(current_player)
				try:
					next(coro)
				except StopIteration:
					pass
				else:
					while True:
						info = yield
						try:
							coro.send(info)
						except StopIteration:
							break

			elif current_player[('hand', idx)].name == 'Throne Room':
				card_to_play = current_player.remove_card('hand', idx)
				current_player.add_cards('in play', card_to_play)
				coro = self.play_action(current_player)
				try:
					next(coro)
				except StopIteration:
					pass
				else:
					while True:
						info = yield
						try:
							coro.send(info)
						except StopIteration:
							break

				card_to_play = current_player.remove_card('in play', -2)
				current_player.add_cards('in play', card_to_play)
				coro = self.play_action(current_player)
				try:
					next(coro)
				except StopIteration:
					pass
				else:
					while True:
						info = yield
						try:
							coro.send(info)
						except StopIteration:
							break

			else:
				card_to_play = current_player.remove_card('hand', idx)
				current_player.add_cards('in play', card_to_play)

				for amt in range(2):
					coro = self.play_action(current_player)
					try:
						next(coro)
					except StopIteration:
						pass
					else:
						while True:
							info = yield
							try:
								coro.send(info)
							except StopIteration:
								break

		elif played_card.name == 'Council Room':
			for amount in range(4):
				current_player.draw_card()
			current_player.buys += 1
			for others in other_players:
				others.draw_card()

		elif played_card.name == 'Festival':
			current_player.actions += 2
			current_player.buys    += 1
			current_player.gold    += 2

		elif played_card.name == 'Laboratory':
			for amount in range(2):
				current_player.draw_card()
			current_player.actions += 1

		elif played_card.name == 'Library':
			set_aside = []
			while current_player.length('hand') < 7:
				if current_player.is_empty('deck'):
					if current_player.is_empty('discard'):
						self.info_list.append('Public:{} cannot draw anymore cards.'.format(current_player.name))
						break
					current_player.transfer_cards('discard', 'deck')
					current_player.shuffle()
				removed_card = current_player.remove_card('deck')
				self.info_list.append('Public:{} drew a {}.'.format(current_player.name, removed_card.name))
				if removed_card.type == 'Action':
					self.info_list.append('Private:{}:Decision:Set aside the {}?:Yes:No'.format(current_player.name, removed_card.name))
					user_input = yield
					if user_input == '0':
						set_aside.append(removed_card)
						self.info_list.append('Public:{} set {} aside.'.format(current_player.name, removed_card.name))
					else:
						current_player.add_cards('hand', removed_card)
						self.info_list.append('Public:{} did not set {} aside.'.format(current_player.name, removed_card.name))
				else:
					current_player.add_cards('hand', removed_card)
			if set_aside != []:
				current_player.add_cards('discard', set_aside)

		elif played_card.name == 'Market':
			current_player.draw_card()
			current_player.actions += 1
			current_player.buys    += 1
			current_player.gold    += 1

		elif played_card.name == 'Mine':
			if current_player.is_empty('hand'):
				self.info_list.append("Public:{}'s hand is empty.".format(current_player.name))
				return

			card_list = [card.name for card in current_player]
			for card in card_list:
				if card in {'Copper', 'Silver', 'Gold'}: break
			else:
				self.info_list.append('Public:{} has no treasures in hand.'.format(current_player.name))
				return

			self.info_list.append('Private:{}:Select:Choose a treasure card to trash.'.format(current_player.name))
			while True:
				idx = yield
				if idx == '':
					self.info_list.append('Private:{}:Error:You must choose a card to trash, try again!'.format(current_player.name))
				else:
					idx = int(idx.split(' ')[0])
					if current_player[('hand', idx)].type == 'Treasure':
						trashed_card = current_player.remove_card('hand', idx)
						self._trash.add_cards(trashed_card)	
						self.info_list.append('Public:{} trashed a {}.'.format(current_player.name, trashed_card.name))
						break
					else:
						self.info_list.append('Private:{}:Error:That is not a treasure card, try again!'.format(current_player.name))
				self.info_list.append('Private:{}:Select:(blank)'.format(current_player.name))

			self.info_list.append('Private:{}:Gain:Gain a treasure card costing up to {}.'.format(current_player.name, trashed_card.cost + 3))		
			while True:
				idx = yield
				if self.gain_card(current_player, trashed_card.cost + 3, int(idx), {'Treasure'}):
					gained_card = current_player.remove_card('discard', -1)
					current_player.add_cards('hand', gained_card)
					break
				self.info_list.append('Private:{}:Gain:(blank)'.format(current_player.name))

		elif played_card.name == 'Witch':
			for amount in range(2): current_player.draw_card()
			for others in other_players:
				if moat in others:
					self.info_list.append('Public:{} blocked the attack using Moat.'.format(others.name))
					continue
				if self._curses.is_empty() == False:
					others.add_cards('discard', self._curses.remove_card())
					self.info_list.append('Public:{} gained a Curse.'.format(others.name))
				else:
					self.info_list.append('Public:There are no more Curses. Yay...')
					return

		elif played_card.name == 'Adventurer':
			treasures_revealed = 0
			revealed = []
			while treasures_revealed < 2:
				if current_player.is_empty('deck'):
					if current_player.is_empty('discard'):	
						self.info_list.append('Public:{} cannot draw anymore cards.'.format(current_player.name))
						break
					current_player.transfer_cards('discard', 'deck')
					current_player.shuffle()

				temp = current_player.remove_card('deck')
				self.info_list.append('Public:{} revealed a {}.'.format(current_player.name, temp.name))
				revealed.append(temp)	
				if revealed[-1].type == 'Treasure':
					current_player.add_cards('hand', revealed.pop())
					treasures_revealed += 1

			if revealed != []:
				current_player.add_cards('discard', revealed)

	def gain_card(self, current_player, cost, idx, card_type=set()):
		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)
	
		if supply[idx].is_empty() == False:
			if supply[idx][-1].type in card_type:
				if supply[idx][-1].cost <= cost:
					gained_card = supply[idx].remove_card()
					current_player.add_cards('discard', gained_card)
					self.info_list.append('Public:{} gained a {}.'.format(current_player.name, gained_card.name))
					return True
				else:
					self.info_list.append('Private:{}:Error:That card costs more than {}, try again!'.format(current_player.name, cost))
					return False
			else:
				self.info_list.append('Private:{}:Error:You cannot gain a card of that type, try again!'.format(current_player.name))
				return False
		else:
			self.info_list.append('Private:{}:Error:That supply pile is empty, try again!'.format(current_player.name))
			return False

	def end_game(self):
		# calculates the final score for each player
		ret = ''
		for temp in self._players:
			ret += temp.calc_score() + '<br>'
		self.info_list.append('End Game:{}'.format(ret))

	def supply_string(self):
		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)
		pile_string = ''
		for pile in supply:
			if pile.is_empty() == False:
				pile_string += pile[-1].name + ',' + str(len(pile))
			else:
				pile_string += 'Blank' + ',0'
			if pile != supply[-1]:
				pile_string += ','

		return pile_string

	def hand_string(self, idx):
		if self._players[idx].is_empty('hand'):
			return '(blank)'
		return ','.join(card.name for card in self._players[idx])

	def stats_string(self, idx):
		p = self._players[idx]
		return ','.join(str(stats) for stats in (p.actions, p.gold, p.buys))

	def deck_string(self, idx):
		if self._players[idx].is_empty('deck'):
			return 'Blank,0'
		return 'Back,' + str(self._players[idx].length('deck'))

	def discard_string(self, idx):
		if self._players[idx].is_empty('discard'):
			return 'Blank,0'
		return self._players[idx][('discard', -1)].name + ',' + str(self._players[idx].length('discard'))

	def curse_string(self):
		if self._curses.is_empty():
			return 'Blank,0'
		return 'Curse,' + str(len(self._curses))

	def trash_string(self):
		if self._trash.is_empty():
			return 'Trash,0'
		return self._trash[-1].name + ',' + str(len(self._trash))
