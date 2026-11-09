# PassGen Vault
![Python](https://img.shields.io/badge/python-3.14-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)

A small desktop password manager written in Python. It generates random passwords, stores them encrypted in a local SQLite database, and protects everything with a single master password. The GUI is built with `tkinter`.

> Educational project. It has not been audited. Do not use it as your only copy of important passwords.

## Features

- Cryptographically secure password generation (`secrets`)
- Configurable length (minimum 12, default 16), optional digits and special characters
- Passwords encrypted at rest, unlocked by a master password
- Master password confirmation when the vault is created
- Per-service, per-username records with overwrite confirmation
- Retrieve all records for a service, delete a single record
- Generated password copied to the clipboard and cleared after 60 seconds (only if the clipboard still holds that password)

## How it works

### Password generation

`generator.generate(length, numbers, specialchar)` always includes at least one letter, plus one digit and one special character when those options are enabled. The remaining characters are drawn from the full allowed alphabet, then the whole list is shuffled with `secrets.SystemRandom`. Lengths below 12 raise `ValueError`.

### Encryption

| Element | Choice |
|---|---|
| Key derivation | PBKDF2-HMAC-SHA256, 600,000 iterations, 16-byte random salt |
| Encryption | Fernet (AES-128-CBC with HMAC-SHA256 authentication) |
| Master password check | A "canary" value (`VALID`) is encrypted and stored in `verify.key`; a wrong password fails to decrypt it |
| Storage | SQLite, table `vault(service, username, encrypted_password)` with a `UNIQUE(service, username)` constraint |

The master password itself is never stored. Only the salt and the encrypted canary are kept next to the database.

### Data location

All data lives in `~/.passgen_vault/`:

```
~/.passgen_vault/
├── passwords.db   # SQLite database with encrypted passwords
├── salt.key       # random salt for key derivation
└── verify.key     # encrypted canary used to check the master password
```

On POSIX systems the directory is created with `0700` and the key files with `0600`.

**Back up all three files together.** Without `salt.key` and `verify.key` the database cannot be decrypted.

## Requirements

- Python 3.14 or newer
- `tkinter` (bundled with most Python installers; on Debian/Ubuntu: `sudo apt install python3-tk`)
- [`cryptography`](https://pypi.org/project/cryptography/)
- [`pyperclip`](https://pypi.org/project/pyperclip/) (on Linux it also needs `xclip` or `xsel`)

## Installation

Run the commands from the project root.

With [uv](https://docs.astral.sh/uv/):

```bash
git clone <repository-url>
cd randompasswordgenerator
uv sync
```

Or with pip:

```bash
git clone <repository-url>
cd randompasswordgenerator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install cryptography pyperclip
```

## Usage

```bash
uv run passgen
```

1. **First launch:** choose a master password (at least 12 characters) and repeat it. **It cannot be recovered.**
2. **Later launches:** enter the master password to unlock the vault.
3. **Generate:** fill in *Service* and *Username*, set the length and options, click *Generate Password*. The password is saved and copied to the clipboard for 60 seconds.
4. **Retrieve:** enter a *Service* and click *Retrieve Records For Given Service* to see all stored usernames and passwords for it.
5. **Delete:** enter *Service* and *Username* and click *Delete Record*.

## Tests

The project has a [pytest](https://docs.pytest.org/) suite covering the generator and the vault manager. Vault tests run against a temporary directory, so your real `~/.passgen_vault` is never touched.

```bash
pip install pytest      # or: uv add --dev pytest
pytest -v
```

Covered cases include password length and character rules, minimum length validation, storing, overwriting and deleting records, wrong master password, persistence after reopening, no plain-text passwords in the database, and corrupted records.

## Project structure

```
randompasswordgenerator/        
├── pyproject.toml
├── README.md
├── .gitignore
├── .python-version
├── src/
│   └── randompasswordgenerator/
│       ├── __init__.py
│       ├── main.py
│       ├── gui.py
│       ├── manager.py
│       ├── generator.py
│       └── clear_clipboard.py
└── tests/
    ├── test_generator.py
    └── test_manager.py
```

## Security notes and limitations

- **The master password cannot be recovered.** If you forget it, the stored passwords are lost.
- **In case of lost password** deletion of all files in directory `~/.passgen_vault` is needed.
- Only passwords are encrypted. `service` and `username` are stored in plain text in the database.
- Retrieved passwords are displayed in a dialog window, so be mindful of shoulder surfing.
- Clipboard clearing relies on a timer inside the running app. If you close the application before the 60 seconds pass, the password stays in the clipboard.
- Clipboard managers and other software with clipboard access may keep their own history of copied passwords.
- No protection against keyloggers, malware, or memory dumps on a compromised machine.
- No auto-lock: the vault stays unlocked until the application is closed.
- If `verify.key` or `salt.key` is deleted while the database remains, existing records can no longer be decrypted.

## Possible improvements

- Copy retrieved passwords to the clipboard instead of showing them
- List of stored services instead of typing names
- Auto-lock after inactivity
- Master password change (re-encrypting all records)
