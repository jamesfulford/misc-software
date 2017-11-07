# Rotary Encrypt Files.py
# by James Fulford
# first argument is the keys to load

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

import encrypt
import encrypt.encoder
import sys
import os
import json


def encrypt_files(filepaths, keys, engine, replace=False, encoder=encrypt.encoder.Static()):
    files = []
    for file in filepaths:
        if os.path.exists(file):
            files.append(file)
        else:
            print("Given filepath could not be found: " + file)
    for path in files:
        message = ""
        with open(path) as phile:
            message = phile.read()
        engine.setkeys(keys)
        cipher = engine.encrypt(message)
        name = path
        if not replace:
            name += ".json"
        with open(name, "wb") as phile:
            if encoder:
                cipher = encoder.encode(cipher)
            phile.write(json.dumps(cipher))
        print("Complete: " + path)



if(len(sys.argv) < 3):  # note that this script's name counts as an argument
    print("Insufficient arguments.")
    print("Please supply a file to source keys from,")
    print("Plus at least a single file to encrypt.")
    print("Enter to ENCRYPT:")
    print("python \"" + __file__ + "\" <keys>.json <*files>")
else:
    keypath = sys.argv[1]
    keys = encrypt.RotarySettings.load(keypath)
    filepaths = sys.argv[2:]
    encrypt_files(filepaths, keys, encrypt.Rotary(keys))
