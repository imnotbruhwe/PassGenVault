def TrueOrFalse(input):
    input = input.lower()
    if input == 'y':
        return True
    elif input == 'n':
        return False
    else:
        raise ValueError