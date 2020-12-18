

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
    into a string of characters representing the custom seed and write it to the text file specified by
    the user."""

    # the text file name specified by the user that we want to write to
    # if the specified text file already has contents, then the contents are overwritten
    # if the specified text file does not yet exist, then it is created
    text_file = input("Please enter the name of the text file to write the seed to: ")

    # the reference to the user specified text file
    f = open(text_file, "w+")

    # start = '1' if the first tile is an obstacle, and '0' if first tile is not obstacle
    start = '1'

    # create list l with the integers that we will later convert to characters to represent custom environment
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

    # convert integers in list l to characters to create the string and write the string onto file f with
    # specified prefix start
    f.write(start + convertToMap(l))


main()