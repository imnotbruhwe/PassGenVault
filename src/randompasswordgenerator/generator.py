import string
import secrets


def generate(length=16, numbers=True, specialchar=True):
    password = []
    if length < 12:
        raise ValueError("The password must be at least 4 characters long.")
    alphabet = string.ascii_letters
    litera = secrets.choice(alphabet)
    password.append(litera)
    count = 1

    if numbers:
        nums = string.digits
        numer = secrets.choice(nums)
        password.append(numer)
        alphabet += nums
        count += 1

    if specialchar:
        spec = string.punctuation
        znak = secrets.choice(spec)
        password.append(znak)
        alphabet += spec
        count += 1

    for i in range(length - count):
        addd = secrets.choice(alphabet)
        password.append(addd)

    rng = secrets.SystemRandom()
    rng.shuffle(password)
    final_password = "".join(password)
    return final_password
