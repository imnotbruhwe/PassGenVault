import sqlite3

import pytest

from randompasswordgenerator import manager

MASTER = "correct horse battery staple"


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    """Redirect all vault files to a temporary directory."""
    monkeypatch.setattr(manager, "APP_DIR", tmp_path)
    monkeypatch.setattr(manager, "DB_PATH", tmp_path / "passwords.db")
    monkeypatch.setattr(manager, "SALT_PATH", tmp_path / "salt.key")
    monkeypatch.setattr(manager, "VERIFY_PATH", tmp_path / "verify.key")
    return tmp_path


@pytest.fixture
def open_vault(vault_dir):
    """Factory that opens a vault and closes every opened one afterwards."""
    opened = []

    def _open(password=MASTER):
        vault = manager.VaultManager(password)
        opened.append(vault)
        return vault

    yield _open

    for vault in opened:
        if hasattr(vault, "close"):
            vault.close()


def test_creating_vault_creates_key_files(vault_dir, open_vault):
    open_vault()
    assert (vault_dir / "salt.key").exists()
    assert (vault_dir / "verify.key").exists()
    assert (vault_dir / "passwords.db").exists()


def test_vault_exists_helper(vault_dir, open_vault):
    assert not manager.vault_exists()
    open_vault()
    assert manager.vault_exists()


def test_store_and_retrieve_password(open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "s3cret!")
    assert vault.retrieve_service_records("github") == [("alice", "s3cret!")]


def test_retrieve_unknown_service_returns_empty_list(open_vault):
    vault = open_vault()
    assert vault.retrieve_service_records("nothing") == []


def test_multiple_users_for_one_service(open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "pw1")
    vault.store_password("github", "bob", "pw2")
    records = vault.retrieve_service_records("github")
    assert sorted(records) == [("alice", "pw1"), ("bob", "pw2")]


def test_storing_same_service_and_user_overwrites(open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "old")
    vault.store_password("github", "alice", "new")
    assert vault.retrieve_service_records("github") == [("alice", "new")]


def test_check_service_exists(open_vault):
    vault = open_vault()
    assert not vault.check_service_exists("github", "alice")
    vault.store_password("github", "alice", "pw")
    assert vault.check_service_exists("github", "alice")
    assert not vault.check_service_exists("github", "bob")


def test_delete_existing_record(open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "pw")
    assert vault.delete_password("github", "alice") is True
    assert vault.retrieve_service_records("github") == []


def test_delete_missing_record_returns_false(open_vault):
    vault = open_vault()
    assert vault.delete_password("github", "alice") is False


def test_wrong_master_password_is_rejected(open_vault):
    open_vault()  # creates the vault with MASTER
    with pytest.raises(ValueError):
        open_vault("definitely the wrong password")


def test_data_persists_after_reopening(open_vault):
    first = open_vault()
    first.store_password("github", "alice", "pw")
    if hasattr(first, "close"):
        first.close()

    second = open_vault()
    assert second.retrieve_service_records("github") == [("alice", "pw")]


def test_passwords_are_not_stored_in_plain_text(vault_dir, open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "plain-text-marker")

    conn = sqlite3.connect(vault_dir / "passwords.db")
    (stored,) = conn.execute("SELECT encrypted_password FROM vault").fetchone()
    conn.close()

    assert b"plain-text-marker" not in stored


def test_corrupted_record_raises_dedicated_error(vault_dir, open_vault):
    vault = open_vault()
    vault.store_password("github", "alice", "pw")

    conn = sqlite3.connect(vault_dir / "passwords.db")
    conn.execute("UPDATE vault SET encrypted_password = ?", (b"garbage",))
    conn.commit()
    conn.close()

    with pytest.raises(manager.CorruptedRecordError):
        vault.retrieve_service_records("github")
