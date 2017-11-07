# airships.py

import random
import json

#
# Resource Frequencies and Producers
#

freq_patterns = {
    "12P": (2, 0, [4, 3, 3, 1, 0, 1]),
    "10P": (2, 1, [3, 3, 2, 1, 0, 1]),
    "8P": (3, 1, [3, 2, 1, 1, 0, 1]),
    "6P": (3, 2, [2, 2, 1, 0, 0, 1])
}

producer_resource = {
    "Farm": "Food",
    "Mine": "Iron",
    "Mill": "Wood",
    "Rig": "Oil",
    "Vent": "Hydrogen",
    "Shaft": "Metals"
}


def prod_res(prod):
    return producer_resource[prod]


def res_prod(res):
    for p, r in producer_resource.items():
        if res == r:
            return p


#
# Seasons
#

seasons = [
    "Winter",
    "Spring",
    "Summer",
    "Mid-Summer",
    "Fall",
    "November"
]


def next_season(this_season):
    ind = seasons.index(this_season)
    return seasons[(ind + 1) % len(seasons)]


def pick(key_weights):
    pick = random.uniform(0, sum(key_weights.values()))
    for key in sorted(key_weights.keys()):
        pick -= key_weights[key]
        if pick <= 0:
            return key


#
# Calendar, Droughts, and Market Prices
#

class Economy():
    def __init__(self, calendar):
        self.producer_resource = dict(zip(
            map(lambda r: r[3] if len(r) > 3 else res_prod(r[0]), calendar),
            map(lambda r: r[0], calendar)
        ))
        self.general_abundance = dict(map(lambda r: (r[0], r[2]), calendar))
        self.droughts = {}
        for res in self.producer_resource.values():
            shots = freq_patterns[self.general_abundance[res]][1]
            self.droughts[res] = shots

        # make the grid structure
        self.seasons = {}
        for s in seasons:
            self.seasons[s] = {}
            for r in self.producer_resource.values():
                self.seasons[s][r] = []

        # fill in the values
        for res, peak_season, gen_abundance in map(tuple, calendar):
            pattern = freq_patterns[str(gen_abundance)][2]
            res_base = map(lambda x: x[0], calendar).index(res)

            i = 0
            for p in pattern:
                season = seasons[(peak_season + i) % 6]
                val = [((res_base + sh) % 6) + 1 for sh in range(p)]
                self.seasons[season][res] = val
                i += 1

    def __str__(self):
        s = ""
        for sea in self.seasons.keys():
            s += sea + "\n"
            for r in self.producer_resource.values():
                s += "\t" + r + ": " + str(self.seasons[sea][r]) + "\n"

        return s

    def produce(self, season):
        choice = random.randint(1, 6)
        output = []
        for r, outs in self.seasons[season].items():
            if choice in outs:
                output.append(r)
        return choice, output

    def prod_res(self, prod):
        return self.producer_resource[prod]

    def res_prod(self, res):
        for p, r in self.producer_resource.items():
            if res == r:
                return p

    def res_market_price(self, res):
        return freq_patterns[self.general_abundance[res]][0]


#
# Tile Generator
#

class Map():
    def __init__(self, tile_dist, prod_dist):
        self.tile_distribution = tile_dist
        self.producer_distributions = prod_dist

    def make_tile(self):
        # return tile, producer, position
        tile = pick(self.tile_distribution)
        # print self.producer_distributions[tile]
        prod = pick(self.producer_distributions[tile])
        position = 0
        if prod:
            position = random.randint(1, 6)
        return tile, prod, position

    def producer_frequencies(self):
        # Returns likelihood of each producer (no given tile)
        producers = {}
        tilesum = sum(self.tile_distribution.values())
        for tile in self.tile_distribution.keys():
            tile_freq = self.tile_distribution[tile] / float(tilesum)
            prodsum = sum(self.producer_distributions[tile].values())
            for prod in self.producer_distributions[tile]:
                # Probability of this producer given this tile
                p = self.producer_distributions[tile][prod] / float(prodsum)
                # Absolute probability
                absolute_prob = tile_freq * p  # by "and rule"

                # Add prob to the current tabulation
                try:
                    producers[prod] += absolute_prob
                except KeyError:
                    producers[prod] = absolute_prob

        # make pretty
        for prod in producers.keys():
            producers[prod] = round(producers[prod], 3)

        return producers


class Game():
    def __init__(self, file):
        self.mapping = json.load(file)
        self.name = self.mapping["name"]

        self.map = Map(
            self.mapping["tile_distribution"],
            self.mapping["producer_distributions"]
        )
        self.economy = Economy(self.mapping["calendar"])

james = Game(open("RandomGenerationSchemes/moors.json"))
for i in range(9):
    a, b, c = james.map.make_tile()
    print i + 1, a
    if b or c:
        print "   ", b, "at", c
    print
