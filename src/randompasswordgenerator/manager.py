import sqlite3
from cryptography.fernet import Fernet
import os

def load_or_generate_key():
    key_filename = "master.key"
    if not os.path.exists(key_filename):
        key = Fernet.generate_key()
        with open(key_filename, "wb") as f:
            f.write(key)

    with open(key_filename, "rb") as f:
        return f.read()

def init_db():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def store_password(service, username, raw_password):
    key = load_or_generate_key()
    cipher_suite = Fernet(key)

    password_bytes = raw_password.encode('utf-8')
    ciphertext = cipher_suite.encrypt(password_bytes)

    init_db()
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vault (service, username, encrypted_password)
        VALUES (?,?,?)
    """, (service,username,ciphertext))

    conn.commit()
    conn.close()