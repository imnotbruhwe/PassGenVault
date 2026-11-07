import sqlite3
import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

APP_DIR = Path.home() / ".passgen_vault"
APP_DIR.mkdir(parents=True, exist_ok=True)
if os.name == "posix":
    os.chmod(APP_DIR, 0o700)

DB_PATH = APP_DIR / "passwords.db"
SALT_PATH = APP_DIR / "salt.key"
VERIFY_PATH = APP_DIR / "verify.key"


class VaultManager:
    def __init__(self, master_password: str):
        # 1. Alokacja lub odczyt Soli Kryptograficznej (S)
        if not SALT_PATH.exists():
            salt = os.urandom(16)
            # Atomowy zapis z restrykcyjnymi uprawnieniami
            with open(SALT_PATH, "wb") as f:
                f.write(salt)
            if os.name == "posix":
                os.chmod(SALT_PATH, 0o600)
        else:
            with open(SALT_PATH, "rb") as f:
                salt = f.read()

        # 2. Wyznaczenie Klucza (K) w czasie O(c)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,
        )

        # Transformacja hasła P i generowanie K_final
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
        self.cipher_suite = Fernet(key)

        if not VERIFY_PATH.exists():
            canary_ciphertext = self.cipher_suite.encrypt(b"VALID")
            with open(VERIFY_PATH, "wb") as f:
                f.write(canary_ciphertext)
            if os.name == 'posix':
                os.chmod(VERIFY_PATH, 0o600)
        else:
            with open(VERIFY_PATH, "rb") as f:
                canary_ciphertext = f.read()
            try:
                decrypted_canary = self.cipher_suite.decrypt(canary_ciphertext)
                if decrypted_canary != b"VALID":
                    raise ValueError("Wrong Master Password.")
            except InvalidToken:
                raise ValueError("Wrong Master Password.")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL,
                UNIQUE(service, username)
            )""")
        self.conn.commit()

    def check_service_exists(self, service, username):
        self.cursor.execute(
            "SELECT id FROM vault WHERE service=? AND username=?", (service, username)
        )
        return self.cursor.fetchone() is not None

    def store_password(self, service, username, raw_password):
        password_bytes = raw_password.encode("utf-8")
        ciphertext = self.cipher_suite.encrypt(password_bytes)
        self.cursor.execute(
            """
            INSERT INTO vault (service, username, encrypted_password)
            VALUES (?, ?, ?) ON CONFLICT(service, username) DO
            UPDATE SET username=excluded.username, encrypted_password=excluded.encrypted_password
            """,
            (service, username, ciphertext),
        )
        self.conn.commit()

    def retrieve_service_records(self, service):
        self.cursor.execute("""
            SELECT username, encrypted_password
            FROM vault
            WHERE service=?""",(service,))

        records = self.cursor.fetchall()

        results_list = []

        for record in records:
            username = record[0]
            encrypted_password = record[1]
            try:
                decrypted = self.cipher_suite.decrypt(encrypted_password).decode('utf-8')
                results_list.append((username,decrypted))
            except InvalidToken:
                return False

        return results_list

    def delete_password(self, service, username):
        self.cursor.execute(
            "DELETE FROM vault WHERE service = ? AND username = ?", (service, username)
        )
        deleted_rows = self.cursor.rowcount
        self.conn.commit()
        return deleted_rows > 0

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
