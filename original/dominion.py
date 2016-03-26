import cards
import player
from copy import copy
from random import shuffle
from itertools import cycle

class Dominion:
	"""A class to represent the game of Dominion. 2 to 4 players.
	   Manages the supply piles and player turns."""

	def __init__(self, player_count=2):
		# initializes the decks and supply piles
		assert player_count in {2, 3, 4}

		self._players = []
		for idx in range(player_count):
			self._players.append(player.Player('Player {}'.format(idx+1)))

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

	def __len__(self):
		# returns the total number of supply piles that are not empty
		total = 0
		for supply in [self._treasures, self._victories, self._kingdoms]:
			for piles in supply:
				if piles.is_empty() == False:
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
		victory_amount = {2: 8, (3,4): 12}
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
			pile.add_cards([copy(randomizers[pile_num]) for amount in range(10)])
			self._kingdoms.append(pile)

	def start_game(self):
		# the main loop of the game, cycles through all players until game is over
		# each player chooses to play a card from hand or several other options
		for current_player in cycle(self._players):
			print("It is {}'s turn!".format(current_player.name))
			current_player.actions = 1
			current_player.buys    = 1
			current_player.gold    = 0
			while current_player.buys > 0:
				current_player.display_hand()
				print('\nA. Play all treasures\n',
					    'B. Buy card\n',
					    'C. Display supply piles\n',
					    'D. Display trash\n',
					    'E. End turn', sep = '')
				current_player.display_stats()
	
				user_input = input('> ')
				if user_input.isdigit() == True:
					user_input = int(user_input)
					if 0 <= user_input < current_player.length('hand'):
						self.play_card(current_player, user_input)
					else:
						print('Invalid choice, try again!')
						continue
				elif user_input in {'a', 'A'}:
					self.play_all_treasures(current_player)
				elif user_input in {'b', 'B'}:
					self.buy_card(current_player)
				elif user_input in {'c', 'C'}:
					self.display_cards()
				elif user_input in {'d', 'D'}:
					print('Cards in trash:\n', self._trash, sep='')
				elif user_input in {'e', 'E'}:
					break
				else:
					print('Invalid choice, try again!')
					continue

			current_player.end_turn()
			# end the game if all provinces or 3 supply piles are empty
			if self._victories[2].is_empty() or len(self) <= 13:
				self.end_game()

	def display_cards(self):
		# displays info for all cards in the supply piles
		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)
		print('Idx', ' ', 'Name', ' '*9, 'Type', ' '*6, 'Cost', ' '*2, 'Rem.', sep='')
		for idx, pile in enumerate(supply):
			if pile.is_empty() == True:
				print('{}. Empty'.format(idx))
			else:
				print('{0:2}. {1:12} {2:8} {3:2} {4:6}'.format(
					   idx, pile[-1].name, pile[-1].type, pile[-1].cost, len(pile)))

	def play_card(self, current_player, idx):
		# play a card from hand
		if current_player[('hand', idx)].type == 'Action':
			if current_player.actions == 0:
				print('You have no more actions, try again!')
				return

		if current_player[('hand', idx)].type == 'Victory':
			print('You cannot play a victory card, try again!')
			return

		if current_player[('hand', idx)].type == 'Curse':
			print('You cannot play a Curse, try again!')
			return

		card_to_play = current_player.remove_card('hand', idx)
		current_player.add_cards('in play', card_to_play)

		if current_player[('in play', -1)].type == 'Treasure':
			self.play_treasure(current_player)
		elif current_player[('in play', -1)].type == 'Action':
			current_player.actions -= 1
			self.play_action(current_player)

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

	def play_all_treasures(self, current_player):
		# play all treasures from hand to increase gold count
		for idx, card in enumerate(current_player):
			if card.name in {'Copper', 'Silver', 'Gold'}:
				self.play_card(current_player, idx)
				self.play_all_treasures(current_player)

	def buy_card(self, current_player):
		self.display_cards()
		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)

		try:
			user_input = int(input('Choose a card to buy: '))
		except ValueError:
			print('Invalid choice, try again!')
			return
		else:
			if 0 <= user_input < len(supply):
				if supply[user_input].is_empty() == False:
					if supply[user_input][-1].cost <= current_player.gold:
						card_to_buy = supply[user_input].remove_card()
						current_player.gold -= card_to_buy.cost
						current_player.buys -= 1
						current_player.actions = 0
						print('{} bought a {}.'.format(current_player.name, card_to_buy.name))
						current_player.add_cards('discard', card_to_buy)
					else:
						print('You cannot afford that card, try again!')
				else:
					print('The supply pile for that card is empty, try again!')
			else:
				print('Invalid choice, try again!')

	def play_action(self, current_player):
		# play an action card from hand
		other_players = set(self._players) - set([current_player])
		played_card = current_player[('in play', -1)]
		moat = cards.Card('Moat', 'Action', 2)
		print('{} played a {}.'.format(current_player.name, played_card.name))

		if played_card.name == 'Cellar':
			current_player.actions += 1
			amount_discarded = 0
			while current_player.length('hand') > 0:
				print("Choose a card to discard. ('q' to quit)")
				current_player.display_hand()
				user_input = self.pick_card(current_player.length('hand'))
				if user_input in {'q', 'Q'}: break
				else:
					discarded_card = current_player.remove_card('hand', user_input)
					print('{} discarded {}.'.format(current_player.name, discarded_card.name))
					current_player.add_cards('discard', discarded_card)
					amount_discarded += 1

			for num in range(amount_discarded):
				current_player.draw_card()
			print('{} drew {} cards.'.format(current_player.name, amount_discarded))

		elif played_card.name == 'Chapel':
			amount_trashed = 0
			while amount_trashed < 4 and current_player.length('hand') > 0:
				print("Choose a card to trash. ('q' to quit)")
				current_player.display_hand()
				user_input = self.pick_card(current_player.length('hand'))
				if user_input in {'q', 'Q'}: break
				else:
					trashed_card = current_player.remove_card('hand', user_input)
					print('{} trashed {}.'.format(current_player.name, trashed_card.name))
					self._trash.add_cards(trashed_card)
					amount_trashed += 1

		elif played_card.name == 'Moat':
			for amount in range(2): current_player.draw_card()

		elif played_card.name == 'Chancellor':
			current_player.gold += 2
			print("Place deck into your discard pile? ('y' for yes)")
			user_input = input('> ')
			if user_input in {'y', 'Y'}:
				current_player.transfer_cards('deck', 'discard')
				print('{} placed deck into discard pile.'.format(current_player.name))

		elif played_card.name == 'Village':
			current_player.draw_card()
			current_player.actions += 2

		elif played_card.name == 'Woodcutter':
			current_player.buys += 1
			current_player.gold += 2

		elif played_card.name == 'Workshop':
			self.gain_card(current_player, 4, {'Treasure', 'Victory', 'Action'})

		elif played_card.name == 'Bureaucrat':
			if self._treasures[1].is_empty() == False:
				gained_silver = self._treasures[1].remove_card()
				print('{} gained a Silver.'.format(current_player.name))
				current_player.add_cards('deck', gained_silver)
			for others in other_players:
				if moat in others:
					print('{} blocked with Moat.'.format(others.name))
					continue
				print(others.name, 'revealed his hand.')
				others.display_hand()
				for idx, card in enumerate(others):
					if card.name in {'Estate', 'Duchy', 'Province'}:
						removed_victory = others.remove_card('hand', idx)
						print('{} placed {} on top of deck.'.format(others.name, card.name))
						others.add_cards('deck', removed_victory)
						break
				else:
					print('{} revealed no victory cards.'.format(others.name))

		elif played_card.name == 'Feast':
			feast = current_player.remove_card('in play')
			self._trash.add_cards(feast)
			self.gain_card(current_player, 5, {'Treasure', 'Victory', 'Action'})

		elif played_card.name == 'Militia':
			current_player.gold += 2
			for others in other_players:
				if moat in others:
					print('{} blocked with Moat.'.format(others.name))
					continue
				while others.length('hand') > 3:
					others.display_hand()
					print('{}, choose a card to discard.'.format(others.name))
					user_input = self.pick_card(others.length('hand'))
					if user_input in {'q', 'Q'}: continue
					else:
						discarded_card = others.remove_card('hand', user_input)
						print('{} discarded {}.'.format(others.name, discarded_card.name))
						others.add_cards('discard', discarded_card)

		elif played_card.name == 'Moneylender':
			for idx, card in enumerate(current_player):
				if card.name == 'Copper':
					trashed_copper = current_player.remove_card('hand', idx)
					print('{} trashed a Copper.'.format(current_player.name))
					self._trash.add_cards(trashed_copper)
					current_player.gold += 3
					return
			else:
				print('There are no coppers in hand to trash.')

		elif played_card.name == 'Remodel':
			if current_player.is_empty('hand'): return
			while True:
				current_player.display_hand()
				print('Choose a card to trash.')
				user_input = self.pick_card(current_player.length('hand'))
				if user_input in {'q', 'Q'}: continue
				else:
					trashed_card = current_player.remove_card('hand', user_input)
					card_cost = trashed_card.cost + 2
					print('{} trashed {}.'.format(current_player.name, trashed_card.name))
					self._trash.add_cards(trashed_card)
					break
	
			self.gain_card(current_player, card_cost, {'Treasure', 'Victory', 'Action'})

		elif played_card.name == 'Smithy':
			for amount in range(3): current_player.draw_card()

		elif played_card.name == 'Spy':
			current_player.draw_card()
			current_player.actions += 1
			for p in self._players:
				if p in other_players:
					if moat in p:
						print('{} blocked with Moat.'.format(p.name))
						continue
				if p.is_empty('deck'):
					if p.is_empty('discard'):
						print('{} cannot reveal a card.'.format(p.name))
						continue
					p.transfer_cards('discard', 'deck')
					p.shuffle()
				revealed_card = p[('deck', -1)]
				print('{} revealed {}.'.format(p.name, revealed_card.name))
				print("Discard? ('y' for yes)")
				user_input = input('> ')
				if user_input in {'y', 'Y'}:
					print('{} discarded {}.'.format(p.name, revealed_card.name))
					revealed_card = p.remove_card('deck')
					p.add_cards('discard', revealed_card)

		elif played_card.name == 'Thief':
			for others in other_players:
				if moat in others:
					print('{} blocked with Moat.'.format(others.name))
					continue
				revealed_cards = []
				for amount in range(2):
					if others.is_empty('deck'):
						if others.is_empty('discard'):
							print('{} cannot reveal anymore cards.'.format(others.name))
							break
						others.transfer_cards('discard', 'deck')
						others.shuffle()
					revealed_cards.append(others._deck.remove_card())

				if revealed_cards == []:
					print('{} had no cards to reveal.'.format(others.name))
					continue

				print('{} revealed the following cards:'.format(others.name))
				for idx, card in enumerate(revealed_cards):
					print('{0}. {1}.'.format(idx, card.name))
				
				while True:
					if (cards.Card('Copper', 'Treasure', 0) in revealed_cards or
						cards.Card('Silver', 'Treasure', 3) in revealed_cards or
						cards.Card('Gold',   'Treasure', 6) in revealed_cards):
						print('Choose a card to trash.')
						user_input = input('> ')
						if user_input == '0':
							if revealed_cards[0].type == 'Treasure':
								trashed_card = revealed_cards.pop(0)
							else:
								print('That is not a treasure card, try again!')
								continue
						elif user_input == '1':
							if revealed_cards[1].type == 'Treasure':
								trashed_card = revealed_cards.pop()
							else:
								print('That is not a treasure card, try again!')
								continue
						else:
							print('Invalid choice, try again!')
							continue
						print('{} trashed {}.'.format(others.name, trashed_card.name))
						self._trash.add_cards(trashed_card)
					break
				if revealed_cards != []:
					others.add_cards('discard', revealed_cards)

				print("Gain the trashed card? ('y' for yes)" )
				user_input = input('> ')
				if user_input in {'y', 'Y'}:
					gained_card = self._trash.remove_card()
					print('{} gained {}.'.format(current_player.name, gained_card.name))
					current_player.add_cards('discard', gained_card)

		elif played_card.name == 'Throne Room':
			if current_player.is_empty('hand'):
				print('There are no cards in your hand.')
				return
			while True:
				print("Choose a card to play twice. ('q' to quit)")
				current_player.display_hand()
				user_input = self.pick_card(current_player.length('hand'))
				if user_input in {'q', 'Q'}: return
				elif current_player[('hand', user_input)].type == 'Action': break
				else:
					print('That is not an Action card, try again!')

			current_player.actions += 1
			# feast and throne room are special cases
			if current_player[('hand', user_input)].name == 'Feast':
				self.play_card(current_player, user_input)
				card_double = self._trash.remove_card()
			elif current_player[('hand', user_input)].name == 'Throne Room':
				self.play_card(current_player, user_input)
				card_double = current_player.remove_card('in play', -2)
			else:
				self.play_card(current_player, user_input)
				card_double = current_player.remove_card('in play')
			current_player.add_cards('hand', card_double)
			current_player.actions += 1
			self.play_card(current_player, -1)

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
						print('You cannot draw anymore cards.')
						break
					current_player.transfer_cards('discard', 'deck')
					current_player.shuffle()
				removed_card = current_player.remove_card('deck')
				print('{} drew {}.'.format(current_player.name, removed_card.name))
				if removed_card.type == 'Action':
					print("Set this card aside? ('y' for yes)")
					user_input = input('> ')
					if user_input in {'y', 'Y'}:
						print('Set {} aside.'.format(removed_card.name))
						set_aside.append(removed_card)
					else:
						current_player.add_cards('hand', removed_card)
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
			if current_player.is_empty('hand'): return
			while True:
				current_player.display_hand()
				print("Choose a treasure card to trash. ('q' to quit)")
				user_input = self.pick_card(current_player.length('hand'))
				if user_input in {'q', 'Q'}: return
				elif current_player[('hand', user_input)].type == 'Treasure':
					trashed_card = current_player.remove_card('hand', user_input)
					card_cost = trashed_card.cost + 3
					print('{} trashed {}.'.format(current_player.name, trashed_card.name))
					self._trash.add_cards(trashed_card)
					break
				else:
					print('That is not a treasure card, try again!')
			self.gain_card(current_player, card_cost, {'Treasure'})
			current_player.add_cards('hand', current_player.remove_card('discard'))

		elif played_card.name == 'Witch':
			for amount in range(2): current_player.draw_card()
			for others in other_players:
				if moat in others:
					print('{} blocked with Moat.'.format(others.name))
					continue
				if self._curses.is_empty() == False:
					print('{} gained a Curse. Go fuck yourself!'.format(others.name))
					others.add_cards('discard', self._curses.remove_card())
				else:
					print('There are no more Curses.')
					return

		elif played_card.name == 'Adventurer':
			treasures_revealed = 0
			revealed = []
			while treasures_revealed < 2:
				if current_player.is_empty('deck'):
					if current_player.is_empty('discard'):	
						print('You cannot draw anymore cards.')
						break
					current_player.transfer_cards('discard', 'deck')
					current_player.shuffle()

				temp = current_player.remove_card('deck')
				print('{} revealed {}.'.format(current_player.name, temp.name))
				revealed.append(temp)	
				if revealed[-1].type == 'Treasure':
					current_player.add_cards('hand', revealed.pop())
					treasures_revealed += 1

			if revealed != []:
				current_player.add_cards('discard', revealed)

	def gain_card(self, current_player, cost=0, card_type=set()):
		self.display_cards()
		supply = []
		supply.extend(self._treasures + self._victories + self._kingdoms)
		while True:
			print('Gain a card costing up to {}.'.format(cost))
			user_input = input('> ')
			if user_input.isdigit():
				user_input = int(user_input)
				if 0 <= user_input < len(supply):
					if supply[user_input].is_empty() == False:
						if supply[user_input][-1].cost <= cost:
							if supply[user_input][-1].type in card_type:
								gained_card = supply[user_input].remove_card()
								print('{} gained {}.'.format(current_player.name, gained_card.name))
								current_player.add_cards('discard', gained_card)
								return
							else:
								print('Wrong type, try again!')
						else:
							print('That card costs more than {}, try again!'.format(cost))
					else:
						print('That pile is empty, try again!')
				else:
					print('Invalid choice, try again!')
			else:
				print('Invalid choice, try again!')

	def pick_card(self, length):
		while True:
			user_input = input('> ')
			if user_input.isdigit():
				user_input = int(user_input)
				if 0 <= user_input < length:
					return user_input
				else:
					print('Invalid choice, try again!')
			elif user_input in {'q', 'Q'}:
				return user_input
			else:
				print('Invalid choice, try again!')

	def end_game(self):
		# calculates the final score for each player and exit the program
		print("The game is over, here's the final score!\n", '-' * 15, sep='')
		for temp in self._players:
			print('{0}: {1:3}'.format(temp.name, temp.calc_score()))
		print('-' * 15)
		raise SystemExit

if __name__ == "__main__":
	game = Dominion()
	game.start_game()