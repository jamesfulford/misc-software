# Cryptonite
Encryption package and scripts in Python.

Package: encrypt
  Interfaces for 
    encoder (strings to integers and back), 
    encryptor (integers to integers), 
    settings (keys), and 
    engines (brings all above parts together)
  Implementation for
    StaticEncoder (handles Unicode-integer conversions)
    Rotary (rotor-based encryption; Enigma minus the plugboard and "weather"/"hail hitler" problems)
    RotarySettings (holds rotors and references, can be saved or loaded to/from file (json is awesome).)  
    
Scripts:
  Rotary: (Defaults to 2^9 to 2^10 rotors of 256 entries each: about 10^1234 to 10^2467 brute force calculations required)
    Encrypt Files:
      Provide keys file and any number of files >=1 to encrypt as command line arguments,
      and it will place encrypted files right next to those files (with an extra .json on the end of the name)
    Decrypt Files:
      Provide keys file and any number of files >=1 to decrypt as command line arguments,
      and it will place decrypted files right next to encrypted files (with an extra .txt on the end of the name)
    Generate Rotary Keys:
      Provide paths >=1 to place random keys into.
