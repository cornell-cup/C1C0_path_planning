

def convertToMap(lens: list):
    """Converts list lens, which contains integers, into their character equivalents and creates a
    a string containing all those characters in order. This will be the content that goes into the
    .txt file containing the seed for a custom map."""
    x = ""
    for i in lens:
        x+=chr(i)
    return x

def main():
    """Edit the contents of this function in order to create a custom map. Append integers representing each
    character that you want in the custom seed onto list l. Then, this will convert this list of ints
    into a string of characters representing the custom seed."""
    l = []

    for i in range(30):
        l.append(130)
        l.append(70)

    l.append(200*10)

    for i in range(100):
        l.append(100)
        l.append(100)

    for i in range(60):
        l.append(40)
        l.append(20)
        l.append(110)
        l.append(30)

    print(convertToMap(l))

main()