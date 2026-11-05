import pyperclip


def clear_clip():
    pyperclip.copy("")
    print("\n[SAFETY FEATURE] Clipboard has been cleared.")
