def TrueOrFalse(input):
    low = input.lower()
    if low == "y":
        return True
    elif low == "n":
        return False
    else:
        raise ValueError
