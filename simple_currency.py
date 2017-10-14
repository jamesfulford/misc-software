# simple_currency.py
# by James Fulford
# converts currencies by retriving conversion data and using inheritance and classes.
# began 6/19/2016
# ended 6/19/2016

import urllib
import json
from credentials import credentials

print("Requesting data from Open Exchange Rates.")
url = "https://openexchangerates.org/api/latest.json?app_id={}"
response = urllib.urlopen(url.format(credentials["openexchangerates"]["app_id"]))
conversions = json.load(response)["rates"]  # this is a dictionary of the most recent conversion rates.
# what the 3 letters mean: https://oxr.readme.io/docs/supported-currencies
print("Retrieved data from Open Exchange Rates. \n \n")


class Currency(object):
    """Mother of all currency classes"""

    def __init__(self, amount):
        assert type(amount) == float or type(amount) == int, amount
        self.amount = amount

    def __str__(self):
        return str(self.__class__.__name__) + ": " + str(self.amount)

    def get_rate(self):
        return conversions[self.__class__.__name__]

    def convert_to(self, currency):
        value = self.amount
        value *= conversions[str(currency.__name__)]
        value /= self.get_rate()
        returningValue = currency(value)
        printing_value = str(self.amount) + " " + str(self.__name__) + " converted to " + str(returningValue)
        print(printing_value)
        return returningValue

    convert = exchange = exchange_to = convert_to


class USD(Currency):
    """United States Dollars"""
    __name__ = "USD"


class CAD(Currency):
    """Canadian Dollars"""
    __name__ = "CAD"


class EUR(Currency):
    """The Euro"""
    __name__ = "EUR"


class BTC(Currency):
    """Bitcoin"""
    __name__ = "BTC"


class GBP(Currency):
    """British Pound"""
    __name__ = "GBP"

currencies = [USD, CAD, EUR, BTC, GBP]

###################################################################################################


USD(20).exchange(CAD)  # sample: converting 20 USD (U.S. Dollars) for CAD (Canadian Dollars)

MONEY = EUR(27.90)
money_converted = []
for currency in currencies:
    money_converted.append(MONEY.convert_to(currency))


money_converted.sort(key=lambda x: x.amount)
for exchange in money_converted:
    print(exchange)

