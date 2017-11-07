# engine.py
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

import encryptor
import encoder


class Engine():
    """
    encrypt.engine.Engine
    Abstract class for all encryption engines.
    """
    def encrypt(self, message):
        messages = self.encoder.encode(message)
        ciphers = self.encryptor.encrypt(messages)
        return self.encoder.decode(ciphers)

    def decrypt(self, cipher):
        ciphers = self.encoder.encode(cipher)
        messages = self.encryptor.decrypt(ciphers)
        return self.encoder.decode(messages)

    def setkeys(self, keys):
        self.encryptor.setkeys(keys)


class Rotary(Engine):
    """
    encrypt.engine.Rotary
    Uses Rotary and Static encoder.
    """
    def __init__(self, keys):
        self.encryptor = encryptor.Rotary(keys)
        self.encoder = encoder.Static()
