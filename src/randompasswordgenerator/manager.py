import sqlite3
from cryptography.fernet import Fernet
import os
import pyperclip
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
            service TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def check_service_exists(service):
    init_db()
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM vault
        WHERE service=?""",(service,))

    record = cursor.fetchone()
    conn.close()
    if record is not None:
        return True
    else: return False

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
        ON CONFLICT(service) DO UPDATE SET
            username=excluded.username, 
            encrypted_password=excluded.encrypted_password
    """, (service,username,ciphertext))

    conn.commit()
    conn.close()

def retrieve_password(sservice):
    init_db()
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, encrypted_password FROM vault
        WHERE service=?
    """, (sservice,))
    record = cursor.fetchone()
    conn.close()
    if record is not None:
        username = record[0]
        encrypted_password = record[1]
        encryption_key = load_or_generate_key()
        cipher_suite = Fernet(encryption_key)
        decrypted_password = cipher_suite.decrypt(encrypted_password)
        final_password = decrypted_password.decode('utf-8')
        print(f"Username for service {sservice} is: {username}, and the password has been copied to clipboard!")
        pyperclip.copy(final_password)
        return
    else:
        print("This service is not present in the database")
        return


