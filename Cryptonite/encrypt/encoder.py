# encoder.py
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


class Static():
    """
    encrypt.encoder.Static
    Encoder that uses utf-8 to translate characters to integers.
    """
    @staticmethod
    def encode(string):
        """
        encrypt.encoder.Static.encode
        Uses UTF to translate string into a list of integers.
        """
        return map(ord, string)

    @staticmethod
    def decode(ints):
        """
        encrypt.encoder.Static.decode
        Uses UTF to translate list of integers into a string
        """
        return "".join(map(chr, ints))
