import grid
from tkinter import *

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


def updateMap(canvas):
    # TODO
    pass


if __name__ == "__main__":
    wMap = grid.Grid(5, 5, 40)
    wMap.grid[0][0].isObstacle = True
    wMap.grid[3][2].isObstacle = True
    path = set([wMap.grid[0][0], wMap.grid[1][1], wMap.grid[2][2]])
    master, canvas = mapWithPath(wMap, path)
    master.mainloop()
