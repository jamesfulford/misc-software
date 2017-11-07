# Generate Rotary Keys.py
# by James Fulford
# creates standard strength and language encryption keys for use with Rotary

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


import os
import sys
import encrypt


if(len(sys.argv) < 2):  # note this script's name counts as an argument
    print("Insufficient arguments.")
    print("Please supply at least one file to store keys in:")
    print("python \"" + __file__ + "\" <*keys>.json")
else:
    for path in sys.argv[1:]:
        try:
            keys = encrypt.RotarySettings()
            keys.save(path)
            print("Completed: " + path)
        except IOError, e:
            print("Provided path is not a valid path: " + path)
            print(e)