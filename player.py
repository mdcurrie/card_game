import sys
import cards

class Player:
	"""A class to represent a player.
	   Four lists to manage: deck, hand, discard pile, and cards in play."""

	def __init__(self, name=''):
		# initialize name, score, and card lists
		self.name           = name
		self.actions        = 0
		self.gold           = 0
		self.buys           = 0
		self._deck          = cards.Cards()
		self._hand          = cards.Cards()
		self._discard_pile  = cards.Cards()
		self._cards_in_play = cards.Cards()
		self._card_dict = {'hand':    self._hand,
						   'deck':    self._deck, 
						   'discard': self._discard_pile,
						   'in play': self._cards_in_play,}

		# a player starts with three Estates and seven Coppers in deck
		estates = [cards.Card('Estate', 'Victory', 2)  for amount in range(3)]
		coppers = [cards.Card('Copper', 'Treasure', 0) for amount in range(7)]
		self.add_cards('deck', estates)
		self.add_cards('deck', coppers)
		
		# shuffle deck and draw five cards
		self.shuffle()
		self.draw_hand()

	def __repr__(self):
		# returns a string with the name, type, and cost of each card 
		# owned by the player
		ret  = []

		def create_string(card_string, card_list):
			nonlocal ret
			ret.append(card_string)
			ret.append(repr(card_list))
		
		create_string('Cards in hand:', self._hand)
		create_string('\nCards in play:', self._cards_in_play)
		create_string('\nCards in discard pile:', self._discard_pile)
		create_string('\nCards in deck:', self._deck)

		return '\n'.join(ret)

	def __str__(self):
		# returns a string with the name of each card owned by the player
		ret = []

		def create_string(card_string, card_list):
			nonlocal ret
			ret.append(card_string)
			ret.append(str(card_list))

		create_string('Cards in hand:', self._hand)
		create_string('\nCards in play:', self._cards_in_play)
		create_string('\nCards in discard pile:', self._discard_pile)
		create_string('\nCards in deck:', self._deck)

		return '\n'.join(ret)

	def __len__(self, card_list):
		# returns the total number of cards owned by the player
		return sum([len(self._deck),
			        len(self._hand), 
			        len(self._discard_pile),
			        len(self._cards_in_play)])

	def __contains__(self, card):
		# returns True if a given card is in the player's hand
		return card in self._hand

	def __iter__(self):
		# yields all cards in the player's hand
		for card in self._hand: yield card

	def __getitem__(self, list_and_index):
		# returns the card in the specified list given the index
		card_list, idx = list_and_index
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.__getitem__()\n')
		else:
			return card_list[idx]

	def draw_card(self):
		# draw 1 card from the deck and place it in hand
		if self.is_empty('deck') == False:
			self.add_cards('hand', self.remove_card('deck'))
		else:
			if self.is_empty('discard') == True: return

			# transfer all cards from discard pile to deck, shuffle, and draw.
			self.transfer_cards('discard', 'deck')
			self.shuffle()
			self.draw_card()

	def draw_hand(self):
		# draw 5 cards from the deck and place in hand
		for amount in range(5):
			if self.is_empty('deck') and self.is_empty('discard'):
				return
			self.draw_card()

	def end_turn(self):
		# place all cards in hand and in play into the discard pile
		# draw hand for next turn
		self.transfer_cards('hand', 'discard')
		self.transfer_cards('in play', 'discard')
		self.draw_hand()

	def shuffle(self):
		# shuffles the player's deck
		self._deck.shuffle()

	def transfer_cards(self, cards_from, cards_to):
		# transfers all of the cards from one pile to another
		try:
			cards_from = self._card_dict[cards_from]
			cards_to   = self._card_dict[cards_to]
		except KeyError:
			sys.stderr.write('KeyError in Player.transfer_cards()\n')
		else:
			cards_to.add_cards(cards_from.remove_all_cards())

	def is_empty(self, card_list):
		# return True if the given card list is empty
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.is_empty()\n')
		else:
			return card_list.is_empty()

	def add_cards(self, card_list, cards_to_add):
		# add cards to the one of the lists
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.add_cards()\n')
		else:
			card_list.add_cards(cards_to_add)

	def remove_card(self, card_list, idx=-1):
		# remove a single card from one of the lists and return it
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.remove_card()\n')
		else:
			return card_list.remove_card(idx)

	def remove_all_cards(self, card_list):
		# removes all cards from one of the lists and returns them
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.remove_all_cards()\n')
		else:
			return card_list.remove_all_cards()

	def length(self, card_list):
		# returns the total number of cards in the given list
		try:
			card_list = self._card_dict[card_list]
		except KeyError:
			sys.stderr.write('KeyError in Player.length()\n')
		else:
			return len(card_list)

	def calc_score(self):
		# calculates the final score for the player once the game ends
		score_string = '{} -> '.format(self.name)

		self.transfer_cards('hand',    'deck')
		self.transfer_cards('discard', 'deck')
		self.transfer_cards('in play', 'deck')

		def card_count(card): return self._deck.card_count(card)

		# estates are worth 1 point, duchies are worth 3, and provinces are worth 6
		score  = 0
		score += 1 * card_count(cards.Card('Estate', 'Victory', 2))
		score += 3 * card_count(cards.Card('Duchy', 'Victory', 5))
		score += 6 * card_count(cards.Card('Province', 'Victory', 8))

		# curses are worth -1 point
		score += -1 * card_count(cards.Card('Curse', 'Curse', 0))
		
		# gardens are worth 1 point for every 10 cards in the deck
		gardens_count = card_count(cards.Card('Gardens', 'Victory', 4))
		score += (len(self._deck) // 10) * gardens_count

		if cards.Card('Province', 'Victory', 8) in self._deck:
			score_string += '{} Provinces '.format(str(card_count(cards.Card('Province', 'Victory', 8))))
		if cards.Card('Duchy', 'Victory', 5) in self._deck:
			score_string += '{} Duchies '.format(str(card_count(cards.Card('Duchy', 'Victory', 5))))
		if cards.Card('Estate', 'Victory', 2) in self._deck:
			score_string += '{} Estates '.format(str(card_count(cards.Card('Estate', 'Victory', 2))))
		if cards.Card('Gardens', 'Victory', 4) in self._deck:
			score_string += '{} Gardens '.format(str(card_count(cards.Card('Gardens', 'Victory', 4))))
		if cards.Card('Curse', 'Curse', 0) in self._deck:
			score_string += '{} Curses '.format(str(card_count(cards.Card('Curse', 'Curse', 0))))

		score_string += ' = {}'.format(score)

		return score_string