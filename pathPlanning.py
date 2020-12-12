from DynamicSmoothedGUI import *
import search
from tkinter import *
from Consts import *
from RandomObjects import RandomObjects

def validLocation(text: str) -> int:
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
    comma_index = text.find(',')
    first_num = float(text[1:comma_index])
    second_num = float(text[comma_index + 1:-1])
    # convert from meters to cm
    first_num = first_num * 100
    second_num = second_num * 100
    first_num = first_num + tile_num_width * tile_size / 2
    second_num = -second_num + tile_num_height * tile_size / 2

    return (first_num, second_num)

def getCommand(text: str) -> (str, int):
    """
    Precondition: text is a valid command
    Return the paresed command in the form of a (str, int) tuple
    where str is the type of the command and int is the amount
    """
    first_paren_index = text.find('(')
    second_paren_index = text.find(')')
    comma_index = text.find(',')
    first = text[first_paren_index + 1:comma_index]
    second = text[comma_index + 1:second_paren_index]
    return (str(first), float(second))

def isnumeric_custom(text: str) -> bool:
    if text[0] == '-':
        return text[1:].isnumeric()
    else:
        return text.isnumeric()

def validInput(text: str) -> int:
    """
    Takes in text and outputs
        1: if the text is a valid location on the grid size
        2: if the text is a valid command to execute
        3: if the location was outside the grid
        4: the command type was invalid
        5: the amount of the command is invalid
        6: the input is malformed
    """
    try:
        first_paren_index = text.find('(')
        second_paren_index = text.find(')')
        comma_index = text.find(',')
        first = text[first_paren_index + 1:comma_index]
        second = text[comma_index + 1:second_paren_index]
        ret = 6
        if isnumeric_custom(first) and isnumeric_custom(second):
            first_num = float(first)
            second_num = float(second)
            ret = 1
            if first_num > tile_size * tile_num_width / 2 or first_num < -(tile_size * tile_num_width / 2):
                ret = 3
            if second_num > tile_size * tile_num_height / 2 or second_num < -(tile_size * tile_num_height / 2):
                ret = 3
        elif first.isalpha() and isnumeric_custom(second):
            ret = 2
            if first != 'turn' and first != 'forward':
                ret = 4
            if float(second) < -360 or 360 < float(second):    
                ret = 5
        return ret

    except:
        return 6


def userInput():
    printScreen()
    print('Please enter a command you would like C1C0 to execute, this could be of the form ')
    print('(x,y) where x,y is the coordinate of the location you would like C1C0 to go to ')
    print(' (command, amount) where the command is \'turn\' or \'forward\' and the amount is either the degress or the m distance for the corresponding command ')
    text = input(
        "COMMAND INPUT: ")
    text = text.replace(' ', '')
    # ending location
    validity = validInput(text)
    while validity != 1 and validity != 2:
        if validity == 3:
            print("Your location was OUT OF THE RANGE of the specified grid")
        if validity == 4:
            print("Your command type is invalid")
        if validity == 5:
            print("Your command amount is out of the specified range, (0::30m) for forward or (-360::360) for turn")
        if validity == 6:
            print("Your input was MALFORMED")
        text = input( 
            "NEW COMMAND INPUT: ")
        validity = validInput(text)

    if validity == 1:  
        dynamicGridSimulation(getLocation(text))
    if validity == 2:
        commandExecute(getCommand(text))

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

    print(endPoint)
    # Run algorithm to get path
    dists, path = search.a_star_search(
        emptyMap, (midX, midY), endPoint, search.euclidean)
    # start GUI and run animation
    simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint, 0)
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

    if command[0] == 'forward':
        # TODO: THIS IS FILLER CODE FOR WHEN WE CAN
         # Run algorithm to get path
        first_num = 0
        second_num = command[1] * 100
        first_num = first_num + tile_num_width * tile_size / 2
        second_num = -second_num + tile_num_height * tile_size / 2
        endPoint = (first_num + tile_size, second_num + tile_size)
        dists, path = search.a_star_search(
            emptyMap, (midX, midY), endPoint, search.euclidean)
        # start GUI and run animation
        simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint, 0)
        simulation.runSimulation()
    if command[0] == 'turn':
        endPoint = (tile_num_width * tile_size / 2, tile_num_height * tile_size / 2)
        dists, path = search.a_star_search(
            emptyMap, (midX, midY), endPoint, search.euclidean)
        # start GUI and run animation
        simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint, (command[1] + 180) % 360)
        simulation.runSimulation()


    # # Run algorithm to get path
    # dists, path = search.a_star_search(
    #     emptyMap, (midX, midY), endPoint, search.euclidean)
    # # start GUI and run animation
    # simulation = DynamicGUI(Tk(), fullMap, emptyMap, search.segment_path(emptyMap, path), endPoint)
    # simulation.runSimulation()


if __name__ == "__main__":
    userInput()
