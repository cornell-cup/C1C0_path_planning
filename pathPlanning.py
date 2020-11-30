from DynamicSmoothedGUI import *
import search
from tkinter import *
from Consts import *
from RandomObjects import RandomObjects

def validLocation(text) -> int:
    """
    takes in text and outputs 1 if the text is a valid location on the grid,
    ouptuts a 2 if the location is outside of the grid
    outputs a 3 if the location text is malformed
    """
    try:
        commaIndex = text.find(',')
        firstNum = float(text[1:commaIndex])
        print(firstNum)
        secondNum = float(text[commaIndex + 1:-1])
        print(secondNum)
        if firstNum > tile_size * tile_num_width / 2 or firstNum < -(tile_size * tile_num_width / 2):
            return 2
        if secondNum > tile_size * tile_num_height / 2 or secondNum < -(tile_size * tile_num_height / 2):
            return 2
        return 1

    except:
        return 3


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


def validCommand(text) -> int:
    """
    takes in text and outputs 1 if the text is a valid command
    Outputs a 2 if the type of the command is invalid
    Outputs a 3 if the amount of the command is invalid
    Outputs a 4 if the tuple is malformed
    """
    try:
        first_paren_index = text.find('(')
        second_paren_index = text.find(')')
        comma_index = text.find(',')
        command = text[first_paren_index + 1:comma_index]
        amount = text[comma_index + 1:second_paren_index]
        ret = 2
        if command == 'turn':
            ret = 3
            if -360 < amount <= 360:
                ret = 1
        if command == 'forward':
            ret = 3
            # Assume the robot will never drive more than 30 meters forward!
            if 0 < amount < 30:
                ret = 1
        return ret
    except:
        return 4

def userInput():
    printScreen()
    print('Please enter a command you would like C1C0 to execute, this could be of the form ')
    print('(x,y) where x,y is the coordinate of the location you would like C1C0 to go to ')
    print(' (command, amount) where the command is \'turn\' or \'forward\' and the amount is either the degress or the m distance for the corresponding command ')
    text = input(
        "COMMAND INPUT:  ")
    # ending location
    while validLocation(text) != 1 and validCommand(text) != 1:
        if validLocation(text) == 2:
            print("Your location was OUT OF THE RANGE of the specified grid")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y):  ")

        elif validLocation(text) == 3:
            print("Your location input was MALFORMED")
            text = input(
                "Please enter the coordinate you desire CICO to go to in the form (x,y): ")

    dynamicGridSimulation(getLocation(text))

def userInputObstacles():
    ## TODO: ADD DOCSTRING
    text = input(
        "Please enter whether you want dynamic or static obstacles:  ")
    while validUserInputObstacles(text) == "-1":
        print("Your input was MALFORMED")
        text = input(
            "Please enter whether you want dynamic or static obstacles:  ")
    if validUserInputObstacles(text) == "static":
        return "static"
    else:
        return "dynamic"

def validUserInputObstacles(text):
    ## TODO: add doc string
    lowercase_text = text.lower()
    static = lowercase_text.find("static")
    dynamic = lowercase_text.find("dynamic")
    if static != -1:
        return lowercase_text[static: static + 5]
    elif dynamic != -1:
        return lowercase_text[dynamic: dynamic + 6]
    else:
        return "-1"

def dynamicGridSimulation(endPoint):
    """
    Run a dynamic grid simulation that navigates C1C0 to endpoint
    Parameter endPoint: (int, int) that represents the (x,y) coordinate
    """
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(fullMap)

    # You can change the number of every type of object you want
    generator.create_env(22, 0, 0, 22, 9)

    # starting location for middle
    midX = tile_size * tile_num_width / 2
    midY = tile_size * tile_num_height / 2

    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint)
    simulation.runSimulation()

def commandExecute(command):
    """
    Run A command execution with C1C0 that executes the command
    Prameter command: a tuple of (type, amount) where type is the type of command 'forward' 'turn' and amount is the
        corresponding distance or degree to execute for the robot.
    """
    emptyMap = grid.Grid(tile_num_height, tile_num_width, tile_size)
    fullMap = grid.Grid(tile_num_height, tile_num_width, tile_size)

    # Generates random enviroment on the grid
    generator = RandomObjects(fullMap)

    # You can change the number of every type of object you want
    generator.create_env(22, 0, 0, 22, 9)

    # starting location for middle
    midX = tile_size * tile_num_width / 2
    midY = tile_size * tile_num_height / 2

    # Calculate and point and change coordinate system from user inputted CICO @(0,0) to the grid coordinates
    userInputObstacles()
    # Run algorithm to get path
    # TODO Figure out how to simulate a simple command, probably create a new class!
    # dists, path = search.a_star_search(
    #     emptyMap, (midX, midY), endPoint, search.euclidean)
    # # start GUI and run animation
    # simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint, generator.squares)
    # simulation.runSimulation()


if __name__ == "__main__":
    userInput()
