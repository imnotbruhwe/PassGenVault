import argparse
import generator
import manager
import TOF

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
        '-u', '--username',
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
        manager.retrieve_password(args.service)
        return

    if args.username is None:
        parser.error("Username must not be empty!")

    if args.length <= 3:
        parser.error("The length of the password must be greater than 3.")

    if manager.check_service_exists(args.service):
        print("Username and password for this service already exist in the database.\n Do you wish to overwrite them? (y/n):")
        while True:
            try:
                yesorno = input()
                decision = TOF.TrueOrFalse(yesorno)
                break
            except ValueError: print("Wrong input! Please type y(Yes) or n(No).")
        if decision is False:
            return


    result = generator.generate(args.length, args.numbers, args.specialchar)

    print("Your generated password is:")
    print(result)
    manager.store_password(args.service, args.username, result)


if __name__ == '__main__':
    main()