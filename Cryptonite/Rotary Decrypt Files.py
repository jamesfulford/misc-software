# Rotary Decrypt Files.py
# by James Fulford
# decrypts files provided

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


def decrypt_files(filepaths, keys, engine, replace=False, encoder=encrypt.encoder.Static()):
    files = []
    for file in filepaths:
        if os.path.exists(file):
            files.append(file)
        else:
            print("Given filepath could not be found: " + file)

    for path in files:
        message = ""
        with open(path) as phile:
            cipher = phile.read()
            if encoder:
                cipher = encoder.decode(json.loads(cipher))
        message = engine.decrypt(cipher)
        name = path
        if not replace:
            name = path + ".txt"
        with open(name, "wb") as phile:
            phile.write(message)
        print("Completed: " + path)


if(len(sys.argv) < 3):  # note that this script's name counts as an argument
    print("Insufficient arguments.")
    print("Please supply a file to source keys from,")
    print("Plus at least a single file to encrypt.")
    print("Enter to DECRYPT:")
    print("python \"" + __file__ + "\" <keys>.json <*files>")
else:
    keypath = sys.argv[1]
    keys = encrypt.RotarySettings.load(keypath)
    filepaths = sys.argv[2:]
    decrypt_files(filepaths, keys, encrypt.Rotary(keys))