import string

import pytest

from randompasswordgenerator import generator


@pytest.mark.parametrize("length", [12, 16, 32, 64])
def test_length_matches_request(length):
    assert len(generator.generate(length)) == length


@pytest.mark.parametrize("length", [0, 1, 4, 11])
def test_too_short_raises_value_error(length):
    with pytest.raises(ValueError):
        generator.generate(length)


def test_default_length_is_16():
    assert len(generator.generate()) == 16


def test_contains_letter_digit_and_special_when_enabled():
    for _ in range(200):
        password = generator.generate(16, numbers=True, specialchar=True)
        assert any(c in string.ascii_letters for c in password)
        assert any(c in string.digits for c in password)
        assert any(c in string.punctuation for c in password)


def test_no_digits_when_numbers_disabled():
    for _ in range(200):
        password = generator.generate(16, numbers=False, specialchar=True)
        assert not any(c in string.digits for c in password)


def test_no_special_characters_when_disabled():
    for _ in range(200):
        password = generator.generate(16, numbers=True, specialchar=False)
        assert not any(c in string.punctuation for c in password)


def test_only_letters_when_both_disabled():
    for _ in range(200):
        password = generator.generate(16, numbers=False, specialchar=False)
        assert all(c in string.ascii_letters for c in password)


def test_passwords_are_not_repeated():
    passwords = {generator.generate(16) for _ in range(200)}
    assert len(passwords) == 200
