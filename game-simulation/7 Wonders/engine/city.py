# city.py
# by James Fulford

import json

cities = json.load(open("cities.json"))

resources = [
    "wood",
    "ore",
    "stone",
    "brick",
    "cloth",
    "glass",
    "paper"
]


class City():

    played_cards = []  # make sure no None shows up here
    # to avoid free card exploits for cards without prebuilds

    hand = []
    resources = {}
    coins = 0


    def __init__(self, name, side, start_coins=3):
        self.coins = start_coins
        self.get_benefits(cities[name][side]["resources"])

    def get_benefits(self, benefits):
        for bene in benefits.keys():
            if bene in resources:
                try:
                    self.resources[bene] += benefits[bene]
                except KeyError:
                    self.resources[bene] = benefits[bene]

    def can_play(self, card):
        """
        Returns whether given card can be played by this city.
        Cannot play cards you have already built.
        Can build cards you have prebuild for
        Cannot build cards if insufficient resources
        """
        played_cards = map(lambda x: str(x).lower(), self.played_cards)
        if str(card).lower() in played_cards:
            return False
        if card.prebuild in played_cards:
            return True

        for res in card.cost
