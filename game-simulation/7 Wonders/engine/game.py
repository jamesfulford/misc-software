# game.py
# by James Fulford

from deck import Deck
from city import City


james = City("Gizah", "A")

deck = Deck(3)
deck.shuffle()

deck.cards["I"][0].play(james)
