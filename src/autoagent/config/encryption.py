import os
from cryptography.fernet import Fernet

FERNET_SECRET = os.getenv("FERNET_SECRET")
cipher = Fernet(FERNET_SECRET)

def encrypt_value(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    return cipher.decrypt(encrypted_value.encode()).decode()
