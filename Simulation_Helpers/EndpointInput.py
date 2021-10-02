from Constants.Consts import *


def printScreen():
    """
    prints welcome screen to simulation
    """
    # Print screen
    print("_________                            .__  .__    _________")
    print("\_   ___ \  ___________  ____   ____ |  | |  |   \_   ___ \ __ ________  ")
    print("/    \  \/ /  _ \_  __ \/    \_/ __ \|  | |  |   /    \  \/|  |  \____ \ ")
    print("\     \___(  <_> )  | \/   |  \  ___/|  |_|  |__ \     \___|  |  /  |_> >")
    print(" \______  /\____/|__|  |___|  /\___  >____/____/  \______  /____/|   __/ ")
    print("        \/                  \/     \/                    \/      |__|    ")

    print("===================================================================================")
    print("                    Welcome to CICO's path planning Simulation")
    print("===================================================================================")
    print("If you would like to edit the grid size or number of obstacles,")
    print("visit the file consts.py and edit the varaibles located in the python file")


def getLocation(text: str) -> (int, int):
    """
    Precondion: String is a valid string of the form (int,int)
    Returns parsed string in the form of an int tuple
    """
    commaIndex = text.find(',')
    firstNum = float(text[1:commaIndex])
    secondNum = float(text[commaIndex + 1:-1])
    # convert from meters to cm
    firstNum = firstNum * 100
    secondNum = secondNum * 100
    firstNum = firstNum + tile_num_width * tile_size / 2
    secondNum = -secondNum + tile_num_height * tile_size / 2

    return (firstNum, secondNum)


def userInput():
    printScreen()

    text = input(
        "Please enter the coordinate you desire CICO to go to in the form (x,y):  ")
    # ending location
    while (validLocation(text) != 1):
        if (validLocation(text) == 2):
            print("Your location was OUT OF THE RANGE of the specified grid")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y):  ")

        elif (validLocation(text) == 3):
            print("Your location input was MALFORMED")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y): ")

    return getLocation(text)


def validLocation(text) -> int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum = float(text[1:commaIndex])
        secondNum = float(text[commaIndex + 1:-1])
        if (firstNum > tile_size * tile_num_width / 2 or firstNum < -(tile_size * tile_num_width / 2)):
            return 2
        if (secondNum > tile_size * tile_num_height / 2 or secondNum < -(tile_size * tile_num_height / 2)):
            return 2
        return 1

    except:
        return 3
