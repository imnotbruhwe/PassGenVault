import TOF
import generator
def main():
    while True:
            print("Input the length of the password:")
            length = input()
            length = int(length)
            if length <= 3 :
                print("The length of the password must be greater than 3")
            else:
                break
    while True:
        try:
            print("Do you want the password to have numbers? y/n:")
            numbers = TOF.TrueOrFalse(input())
            break
        except ValueError: print("Please try again, type y(Yes) or n(No)")

    while True:
        try:
            print("Do you want the password to have special characters? y/n:")
            specialchar = TOF.TrueOrFalse(input())
            break
        except ValueError: print("Please try again, type y(Yes) or n(No)")

    result = generator.generate(length, numbers, specialchar)
    print("Your password is:")
    print(result)
if __name__ == '__main__':
    main()