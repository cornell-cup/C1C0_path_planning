import grid
from tkinter import *
import time

"""
returns a tuple of a window, canvas widget, and dictionary mapping tiles to rectangle objects
(in that order) that represents the grid object [worldMap]. 
Each tile is represented as a square, tiles that contain
an obstacle are colored red and tiles that are free are colored white. 
"""


def initMap(worldMap):
    master = Tk()
    width = len(worldMap.grid[0]) * worldMap.tileLength
    height = len(worldMap.grid) * worldMap.tileLength
    visMap = Canvas(master, width=width, height=height)
    offset = worldMap.tileLength/2
    tile_dict = {}
    for row in worldMap.grid:
        for tile in row:
            x = tile.x
            y = (len(worldMap.grid)*worldMap.tileLength) - tile.y
            x1 = x - offset
            y1 = y - offset
            x2 = x + offset
            y2 = y + offset
            color = "red" if tile.isObstacle else "white"
            tile_dict[tile] = visMap.create_rectangle(
                x1, y1, x2, y2, fill=color)

    visMap.pack()
    return (master, visMap, tile_dict)


"""
returns a tuple of the window and canvas object representing grid object [worldMap]
with tiles containing an obstacle colored in red and a path of tiles [path] 
colored in green.

Assumes: [path] is an iterable of tile objects that are in [worldMap]
"""


def mapWithPath(worldMap, path):
    master, canvas, tile_dict = initMap(worldMap)
    for tile in path:
        if tile.isObstacle:
            print("ERROR: PATH INCLUDES OBSTACLE")
            break

        rec = tile_dict[tile]
        canvas.itemconfig(rec, fill="green")

    return master, canvas


"""
"""


def updateMap(canvas):
    # TODO
    pass


"""
Creates a gui of grid object [worldMap] with path [path]. If [path] is None then
just creates a gui representation of [worldMap] with obstacles colored red. If 
[path] is an iterable of tiles in [worlMap] then returns a gui representation of
[worldMap] with obstacles colored red and tiles in [path] colored green. [path]
is None by default.
"""


def searchGUI(worldMap, path=None):
    if path:
        master, canvas = mapWithPath(worldMap, path)
    else:
        master, canvas, d = initMap(worldMap)
    master.mainloop()


if __name__ == "__main__":
    master = Tk()
    visMap = Canvas(master, height=200, width=200)
    master.mainloop()
    for i in range(1, 4):
        visMap.create_line(0, 0, i*20, i*20)
        time.sleep(10)
