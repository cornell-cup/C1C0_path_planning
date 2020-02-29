import grid
from tkinter import *

"""
returns a tuple of a window and canvas widget (in that order) that represents the
grid object [worldMap]. Each tile is represented as a square, tiles that contain
an obstacle are colored red and tiles that are free are colored white. 
"""


def initMap(worldMap):
    master = Tk()
    width = len(worldMap.grid[0]) * worldMap.tileLength
    height = len(worldMap.grid) * worldMap.tileLength
    visMap = Canvas(master, width=width, height=height)
    offset = worldMap.tileLength/2
    for row in worldMap.grid:
        for tile in row:
            x = tile.x
            y = (len(worldMap.grid)*worldMap.tileLength) - tile.y
            x1 = x - offset
            y1 = y - offset
            x2 = x + offset
            y2 = y + offset
            color = "red" if tile.isObstacle else "white"
            visMap.create_rectangle(x1, y1, x2, y2, fill=color)

    visMap.pack()
    return (master, visMap)


"""
"""


def updateMap(canvas):
    # TODO
    pass


if __name__ == "__main__":
    wMap = grid.Grid(5, 4, 20)
    wMap.grid[0][0].isObstacle = True
    master, canvas = initMap(wMap)
    master.mainloop()
