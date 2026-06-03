import os
import hashlib
import secrets

pwd = "password2"
salt = os.urandom(32)
hash = hashlib.pbkdf2_hmac(
    "sha256",
    pwd.encode("utf-8"),
    salt,
    150000
)
hex_pwd = salt.hex() + hash.hex()
print(hex_pwd)

salt_hex = hex_pwd[:64]
hash_hex = hex_pwd[64:]

n_salt = bytes.fromhex(salt_hex)
n_hash = bytes.fromhex(hash_hex)

if (secrets.compare_digest(n_hash, hash)):
    print("success!")
else:
    print("Invalid")