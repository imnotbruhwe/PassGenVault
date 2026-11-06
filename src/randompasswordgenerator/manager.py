import sqlite3
from cryptography.fernet import Fernet
import os
from pathlib import Path
import pyperclip
import threading

from randompasswordgenerator import clear_clipboard

# Wyznaczenie absolutnej ścieżki domowej dla środowiska operacyjnego
APP_DIR = Path.home() / ".passgen_vault"

# Idempotentna operacja gwarantująca istnienie wierzchołka w systemie plików
APP_DIR.mkdir(parents=True, exist_ok=True)

# Definicja stałych wektorów dla przestrzeni pamięci masowej
DB_PATH = APP_DIR / "passwords.db"
KEY_PATH = APP_DIR / "master.key"

def load_or_generate_key():
    key_filename = KEY_PATH
    if not os.path.exists(key_filename):
        key = Fernet.generate_key()
        with open(key_filename, "wb") as f:
            f.write(key)

    with open(key_filename, "rb") as f:
        return f.read()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL,
            UNIQUE(service, username)
        )
    """)
    conn.commit()
    conn.close()


def check_service_exists(service, username):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM vault
        WHERE service=? AND username=?""",
        (service, username),
    )

    record = cursor.fetchone()
    conn.close()
    if record is not None:
        return True
    else:
        return False


def store_password(service, username, raw_password):
    key = load_or_generate_key()
    cipher_suite = Fernet(key)

    password_bytes = raw_password.encode("utf-8")
    ciphertext = cipher_suite.encrypt(password_bytes)

    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO vault (service, username, encrypted_password)
        VALUES (?,?,?)
        ON CONFLICT(service, username) DO UPDATE SET
            username=excluded.username, 
            encrypted_password=excluded.encrypted_password
    """,
        (service, username, ciphertext),
    )

    conn.commit()
    conn.close()


def retrieve_password(service, username):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT username, encrypted_password FROM vault
        WHERE service=? AND username=?
    """,
        (service, username),
    )
    record = cursor.fetchone()
    conn.close()
    if record is not None:
        encrypted_password = record[1]
        encryption_key = load_or_generate_key()
        cipher_suite = Fernet(encryption_key)
        decrypted_password = cipher_suite.decrypt(encrypted_password)
        final_password = decrypted_password.decode("utf-8")
        print(
            f"Username for service {service} is: {username}, and the password has been copied to clipboard!\n You have 60 seconds before the clipboard cleans!"
        )
        pyperclip.copy(final_password)
        timer = threading.Timer(60.0, clear_clipboard.clear_clip)
        timer.start()
        return
    else:
        print("This service is not present in the database")
        return


def delete_password(service, username):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM vault WHERE service=? AND username=?
    """,
        (service, username),
    )
    conn.commit()
    conn.close()
    print(f"Record for service: {service} and username: {username} has been removed.")
    return
