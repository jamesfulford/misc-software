# deck.py
# by James Fulford


import json
from card import Card
from card import purples
from copy import deepcopy as dc
import random


# card frequency by number of players
freqI = json.load(open("Age I/age I card frequency.json"))
freqII = json.load(open("Age II/age II card frequency.json"))
freqIII = json.load(open("Age III/age III card frequency.json"))
purp_freq = json.load(open("Age III/purple frequency.json"))
purples = json.load(open("Age III/purple.json"))

freq = {}
for level in freqI.keys():
    freq[level] = {}

for age in [freqI, freqII, freqIII]:
    for level in age.keys():
        for card in age[level].keys():
            freq[level][card] = age[level][card]


class Deck():

    def __init__(self, players):
        assert str(players) in purp_freq.keys()
        assert str(players) in freq.keys()
        self.cards = {"I": [], "II": [], "III": []}
        self.discard = {"I": [], "II": [], "III": []}
        if str(players) == 2:
            raise Exception("Two Player not yet implemented")  # TODO
        else:

            levels = range(3, int(players) + 1)

            for level in levels:
                for card in freqI[str(level)].keys():
                    to_add = [Card(card)] * freq[str(level)][card]
                    self.cards["I"].extend(to_add)

                for card in freqII[str(level)].keys():
                    to_add = [Card(card)] * freq[str(level)][card]
                    self.cards["II"].extend(to_add)

                for card in freqIII[str(level)].keys():
                    to_add = [Card(card)] * freq[str(level)][card]
                    self.cards["III"].extend(to_add)


            choose_cards = purp_freq[str(players)]
            these_purples = dc(purples.keys())

            for i in range(choose_cards):
                ch = random.choice(these_purples)
                these_purples.remove(ch)
                self.cards["III"].append(Card(ch))

    def shuffle(self, age=None):
        """
        Reorders cards in all age decks (unless age specifies proper key)
        i.e. age="III" will shuffle only age III's deck
        """
        if age:
            try:
                random.shuffle(self.cards[age])
            except KeyError:
                raise KeyError("Age is not I, II, or III: " + str(age))
        else:
            for a in range(1, 4):
                self.shuffle(age="I" * a)
