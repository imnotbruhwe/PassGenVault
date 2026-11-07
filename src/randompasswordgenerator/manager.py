import sqlite3
from cryptography.fernet import Fernet
import os
from pathlib import Path

# Wyznaczenie absolutnej ścieżki domowej dla środowiska operacyjnego
APP_DIR = Path.home() / ".passgen_vault"

# Idempotentna operacja gwarantująca istnienie wierzchołka w systemie plików
APP_DIR.mkdir(parents=True, exist_ok=True)

# Definicja stałych wektorów dla przestrzeni pamięci masowej
DB_PATH = APP_DIR / "passwords.db"
KEY_PATH = APP_DIR / "master.key"


class VaultManager:
    def __init__(self):
        if not KEY_PATH.exists():
            key = Fernet.generate_key()
            with open(KEY_PATH, "wb") as f:
                f.write(key)

        with open(KEY_PATH, "rb") as f:
            self.key = f.read()

        self.cipher_suite = Fernet(self.key)

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL,
                UNIQUE(service, username))""")
        self.conn.commit()

    def check_service_exists(self, service, username):
        self.cursor.execute(
            """
            SELECT id FROM vault
            WHERE service=? AND username=?""",
            (service, username),
        )
        return self.cursor.fetchone() is not None

    def store_password(self, service, username, raw_password):

        password_bytes = raw_password.encode("utf-8")
        ciphertext = self.cipher_suite.encrypt(password_bytes)

        self.cursor.execute(
            """
            INSERT INTO vault (service, username, encrypted_password)
            VALUES (?, ?, ?) ON CONFLICT(service, username) DO
            UPDATE SET
                username=excluded.username,
                encrypted_password=excluded.encrypted_password
            """,
            (service, username, ciphertext),
        )
        self.conn.commit()

    def retrieve_password(self, service, username):

        self.cursor.execute(
            """
            SELECT username, encrypted_password
            FROM vault
            WHERE service = ?
              AND username = ?
            """,
            (service, username),
        )
        record = self.cursor.fetchone()
        if record is not None:
            encrypted_password = record[1]

            decrypted_password = self.cipher_suite.decrypt(encrypted_password)
            final_password = decrypted_password.decode("utf-8")
            return final_password
        else:
            return None

    def delete_password(self, service, username):

        self.cursor.execute(
            """
            DELETE
            FROM vault
            WHERE service = ?
              AND username = ?
            """,
            (service, username),
        )

        deleted_rows = self.cursor.rowcount
        self.conn.commit()

        return deleted_rows > 0

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()