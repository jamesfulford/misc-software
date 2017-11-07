# encryptor.py
# by James Fulford

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

import copy
import settings

class Encryptor():
    """
    encrypt.encryptor.Encryptor
    An interface for all encryption algorithms
    """
    def __init__(self, keys):
        """Specify None to generate keys"""
        pass

    def setkeys(self, keys):
        pass

    def encrypt(self, ints):
        pass

    def decrypt(self, ints):
        pass


class Rotary(Encryptor):
    """
    encrypt.encryptor.Rotary
    Modelled after a simplified Enigma machine.
    First programmed in Fall 2016 for Object Oriented Programming in C#
    """
    Settings = settings.RotarySettings
    def __init__(self, keys):
        """Specify None to generate keys"""
        keynes = keys
        if keynes is None:
            keynes = settings.RotarySettings()
        self.setkeys(keynes)

    def setkeys(self, keys):
        keys.validate()
        self.rotors = copy.deepcopy(keys.rotors)
        self.references = copy.deepcopy(keys.references)

    def spin(self):
        def inc_rotor(index):
            try:
                upone = self.references[index] + 1
                self.references[index] = upone % len(self.rotors[index])
                return self.references[index] is 0
            except IndexError:
                return False  # should not spin first wheel when last wheel wraps
                # around, otherwise it never gets to pure position.
        i = 0
        while(inc_rotor(i)):
            i = (i + 1) % len(self.rotors)

    def encrypt(self, ints):
        final = []
        for letter in ints:
            cipher = letter
            for j in range(len(self.rotors)):
                index = (cipher + self.references[j]) % len(self.rotors[j])
                cipher = self.rotors[j][index]
            final.append(cipher)
            self.spin()
        return final

    def decrypt(self, ints):
        final = []
        for letter in ints:
            message = letter
            for j in range(len(self.rotors)):
                i = len(self.rotors) - j - 1
                index = self.rotors[i].index(message)
                message = (index - self.references[i]) % len(self.rotors[i])
            final.append(message)
            self.spin()
        return final
