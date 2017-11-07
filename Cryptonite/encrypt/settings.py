# settings.py
# by James Fulford
# generates, saves, loads, and validates settings
# for various encryption engines

# Copyright 2016 James Patrick Fulford

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import os
import json


class Settings():
    """
    encrypt.settings.Settings
    An interface for any format of settings to be provided to an encryptor
    """

    def __init__(self):
        """Generates random keys. More arguments possible."""
        pass

    def validate(self):
        """Ensures that attributes are properly formed."""
        pass

    def save(self, path):
        pass

    def load(self, path):
        pass


class RotarySettings(Settings):
    """
    encrypt.settings.RotarySettings
    Implementation of Settings interface for Rotary encryptor
    """

    def __init__(self, rtrs=[], refs=[], stren=10, lang=256):
        rotors = rtrs
        references = refs

        # length is the number of rotors there will be
        length = max(len(rotors), len(references))
        if length is 0:
            if stren is 0:
                length = 1
            else:
                length = random.randint(2 ** (stren - 1), 2 ** (stren))

        if len(rotors) < length:  # if there are not enough rotors
            for i in range(length):  # for each rotor
                rotor = []
                choices = range(0, lang)
                for item in range(lang):
                    choice = random.choice(choices)
                    choices.remove(choice)
                    rotor.append(choice)
                rotors.append(rotor)

        if len(references) < length:  # if there are not enough references
            for rotor in rotors:
                references.append(random.randint(0, len(rotor) - 1))

        self.rotors = rotors
        self.references = references
        self.lang = lang
        self.strength = stren

    @staticmethod
    def load(path):
        if(os.path.exists(path)):
            info = {}
            with open(path) as phile:
                info = json.loads(phile.read())
            try:
                lang = info["language_length"]
                s = info["strength"]
                p = info["references"]
                r = info["rotors"]
                return RotarySettings(rtrs=r, refs=p, stren=s, lang=lang)
            except KeyError:
                message = "Given key set cannot be used for "
                message += "Rotary encryption: " + path
                print(message)
        else:
            print("Could not find keys at " + path)

    def save(self, path):
        info = {
            "rotors": self.rotors,
            "references": self.references,
            "strength": self.strength,
            "language_length": self.lang
        }
        with open(path, "wb") as phile:
            phile.write(json.dumps(info, indent=4))

    def validate(self):
        if(len(self.rotors) != len(self.references)):
            message = "Error: references and rotors are not same length."
            exp = Exception(message)
            exp.rotorlen = len(self.rotors)
            exp.referenceslen = len(self.references)
            raise exp

        # length of each rotor the same
        lengths = map(len, self.rotors)
        if(min(lengths) is not max(lengths)):
            exp = Exception("Error: not all rotors are the same length")
            exp.lengths = lengths
            raise exp

        for i in range(len(self.rotors)):
            try:
                self.rotors[i][self.references[i]]
            except IndexError:
                message = "Error: reference " + str(self.references[i])
                message += " from rotor number " + str(i)
                message += " is out of bounds."
                exp = Exception(message)
                exp.index = i
                exp.bad_reference = self.references[i]
                raise exp
