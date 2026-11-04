import string
import secrets

def generate(length = 8, numbers = True, specialchar = True):
    alphabet = string.ascii_letters
    if numbers:
        alphabet += string.digits
    if specialchar:
        alphabet += string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password