import argparse
import threading
import pyperclip

import generator
import manager
import TOF
from randompasswordgenerator import clear_clipboard


def main():
    parser = argparse.ArgumentParser(description="Cryptographically secure password generator.")

    parser.add_argument(
        '-s', '--service',
        required=True,
        help="Service the password will be used for. Put the name in quotes."
    )
    parser.add_argument(
        '-r', '--retrieve',
        action='store_true',
        help="Retrieves the username and password from the db using given service name."
    )
    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help="Deletes the record for given service and username."
    )
    parser.add_argument(
        '-u', '--username',
        required=True,
        help="Username used in the Service"
    )
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=8,
        help="Length of the password (must be strictly greater than 3)."
    )

    parser.add_argument(
        '--no-numbers',
        dest='numbers',
        action='store_false',
        help="Exclude numbers from the generated password."
    )

    parser.add_argument(
        '--no-special',
        dest='specialchar',
        action='store_false',
        help="Exclude special characters from the generated password."
    )


    args = parser.parse_args()

    if args.retrieve:
        manager.retrieve_password(args.service, args.username)
        return

    if args.delete:
        manager.delete_password(args.service, args.username)
        return

    if args.length <= 3:
        parser.error("The length of the password must be greater than 3.")

    if manager.check_service_exists(args.service, args.username):
        print("There already is a record for this service and username in the database.\n Do you wish to overwrite the data? (y/n):")
        while True:
            try:
                yesorno = input()
                decision = TOF.TrueOrFalse(yesorno)
                break
            except ValueError: print("Wrong input! Please type y(Yes) or n(No).")
        if decision is False:
            return


    result = generator.generate(args.length, args.numbers, args.specialchar)

    print(f"Your generated password for service: {args.service} and username:{args.username} has been copied to clipboard!\nYou have 60 seconds before the clipboard cleans!")
    pyperclip.copy(result)
    timer = threading.Timer(60.0, clear_clipboard.clear_clip)
    timer.start()
    manager.store_password(args.service, args.username, result)


if __name__ == '__main__':
    main()