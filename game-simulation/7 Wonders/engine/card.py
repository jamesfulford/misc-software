# card.py
# by James Fulford


import json

# coins gained by discarding one card
discard_value = 3


# card definitions
cardsI = json.load(open("Age I/age I cards.json"))
cardsII = json.load(open("Age II/age II cards.json"))
cardsIII = json.load(open("Age III/age III cards.json"))
purples = json.load(open("Age III/purple.json"))

card_defs = {}
i = 1
for dictionary in [cardsI, cardsII, cardsIII, purples]:
    age = "I" * i
    for entry in dictionary:
        card_defs[entry] = dictionary[entry]
        card_defs[entry]["age"] = age
    i += 1


resources = [
    "wood",
    "ore",
    "stone",
    "brick",
    "cloth",
    "glass",
    "paper"
]


class Card():
    def __init__(self, name):
        if name not in card_defs:
            raise IndexError("Card \"" + name + "\" is not defined!")

        self.name = name
        entry = card_defs[name]

        self.benefit = entry.get("benefit", None)
        self.cost = entry.get("cost", None)
        self.prebuild = entry.get("prebuild", None)

    def play(self, city):
        """
        Plays this card on this city. (Will raise AssertionError if it can't)
        """
        assert city.can_play(self)
        city.played_cards.append(self)
        city.get_benefits(self.benefit)
        if self.prebuild not in map(lambda x: str(x).lower(), city.played_cards):
            city.pay_costs(self.cost)

    def discard(self, city):
        """
        Discards this card. Gains coins for this city
        """
        pass

    def wonder(self, city):
        """
        Plays this card as a wonder for this city
        """
        pass

    def cost(self, city):
        """
        Uses publicly available data to find coin cost of building for given city
        """
        pass

    # def value(self, city, foreign=True):
    #     """
    #     Evaluates point value of given card based on city data.
    #     If city is foreign, will use public data. Otherwise, uses all data
    #     """
    #     pass

    def show(self):
        """
        Prints the card in a human-readable format
        """
        return self.name.title()

    __str__ = __repr__ = show
