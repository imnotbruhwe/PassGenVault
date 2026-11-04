import argparse
import generator


def main():
    parser = argparse.ArgumentParser(description="Cryptographically secure password generator.")

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

    # Krok 3: Analiza wektora V w czasie Θ(1)
    args = parser.parse_args()

    # Krok 4: Walidacja niezmiennika wejściowego (n > 3)
    if args.length <= 3:
        parser.error("The length of the password must be greater than 3.")

    # Krok 5: Wywołanie algorytmu podrzędnego
    result = generator.generate(args.length, args.numbers, args.specialchar)

    print("Your generated password is:")
    print(result)


if __name__ == '__main__':
    main()