import sys
from random import shuffle, SystemRandom
from collections import namedtuple

Card = namedtuple('Card', 'name type cost')

class Cards:
	"""A list of cards. Each item in the list is a named tuple that represents
	   an individual card. This class is used to represent a player's deck,
	   hand, discard pile, and cards in play. It is also used for the supply piles
	   and trash."""

	def __init__(self):
		# initialize the list of cards to be empty
		self._cards = []

	def __repr__(self):
		# returns a string with the name, type, and cost of each card in the list
		ret = []
		for card in self._cards:
			ret.append(str(card))
		return '\n'.join(ret)

	def __str__(self):
		# returns a string with the index and name of each card in the list
		ret = []
		for idx, card in enumerate(self._cards):
			ret.append('{}. {}'.format(idx, card.name))
		return '\n'.join(ret)

	def __getitem__(self, index):
		# allows indexing to be performed on the class
		try:
			return self._cards[index]
		except IndexError:
			sys.stderr.write('IndexError in Cards.__getitem__()\n')

	def __iter__(self):
		# allows iteration to be performed on the class
		for card in self._cards: yield card

	def __contains__(self, card):
		# check if the given card is in the list
		return card in self._cards

	def __len__(self):
		# return the amount of cards in the list
		return len(self._cards)

	def is_empty(self):
		# check if the list is empty
		return self._cards == []

	def card_count(self, card):
		# returns the number of times a given card appears in the list
		return self._cards.count(card)

	def shuffle(self):
		# shuffle the list to randomize order of cards
		shuffle(self._cards, SystemRandom().random)

	def add_cards(self, cards_to_add):
		# add cards to list
		if type(cards_to_add) != list:
			cards_to_add = [cards_to_add]
		self._cards.extend(cards_to_add)
		cards_to_add.clear()

	def remove_card(self, position=-1):
		# remove a card from the list
		try:
			return self._cards.pop(position)
		except IndexError:
			sys.stderr.write('IndexError in Cards.remove_card()\n')

	def remove_all_cards(self):
		# remove all cards from the list
		removed_cards = self._cards[:]
		self._cards.clear()
		return removed_cards
