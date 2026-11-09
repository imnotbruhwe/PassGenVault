import pyperclip


def clear_clip(result):
    if pyperclip.paste() == result:
        pyperclip.copy("")

