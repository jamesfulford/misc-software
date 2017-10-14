# James Fulford
# Celsius Fahrenheit Celsius converter


def toFahrenheit(celsius):
    return (celsius * 1.8 + 32)


def toCelsius(fahrenheit):
    return (fahrenheit - 32) / 1.8


def askForNumber():
    print("Please enter your current measurement:")
    userInput = input()
    try:
        return (float(userInput))
    except ValueError:
        return (askForNumber())

keepAsking = True

while True:
    print("Which measurement would you like to convert to?\n")
    query = input("(F) Fahrenheit | (C) Celsius | (Q) Quit\n").lower()

    if query == "f" or query == "fahrenheit":
        print(toFahrenheit(askForNumber()))
        print("degrees fahrenheit.")
    elif query == "c" or query == "celsius":
        print(toCelsius(askForNumber()))
        print("degrees celsius.")
    elif query == "quit" or query == "q":
        break
    else:
        continue  # these two lines are pointless, really


print("Thank you for converting with us! \n By James Fulford.")
