import grid
import search
import tkinter as tk
from tkinter import *
import time
import datetime


class MapPath():
    def __init__(self, master, inputMap, path):
        self.master = master

        self.tile_dict = None
        self.canvas = None
        self.path = path
        self.pathLength = len(path)
        self.pathIndex = 0

        self.create_widgets(inputMap)

    def create_widgets(self, worldMap):
        width = len(worldMap.grid[0]) * worldMap.tileLength
        height = len(worldMap.grid) * worldMap.tileLength
        visMap = Canvas(self.master, width=width, height=height)
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
        self.canvas = visMap
        self.tile_dict = tile_dict

    def updateGrid(self):
        if(self.pathIndex != self.pathLength-1):
            rec = self.tile_dict[self.path[self.pathIndex]]
            self.canvas.itemconfig(rec, fill="green")
            self.pathIndex = self.pathIndex+1
            self.master.after(1000, self.updateGrid)

    def runSimulation(self):
        self.updateGrid()
        self.master.mainloop()


def clock():
    time = datetime.datetime.now().strftime("Time: %H:%M:%S")
    # lab.config(text=time)
    #lab['text'] = time
    root.after(1000, clock)  # run itself again after 1000 ms


if __name__ == "__main__":
    wMap = grid.Grid(10, 10, 40)
    wMap.grid[1][1].isObstacle = True
    wMap.grid[1][2].isObstacle = True
    wMap.grid[1][3].isObstacle = True
    wMap.grid[1][4].isObstacle = True
    wMap.grid[3][0].isObstacle = True
    wMap.grid[3][1].isObstacle = True
    wMap.grid[3][2].isObstacle = True
    wMap.grid[3][3].isObstacle = True
    wMap.grid[5][1].isObstacle = True
    wMap.grid[5][2].isObstacle = True
    wMap.grid[5][3].isObstacle = True
    wMap.grid[5][4].isObstacle = True
    wMap.grid[5][5].isObstacle = True
    wMap.grid[5][6].isObstacle = True
    wMap.grid[5][6].isObstacle = True
    wMap.grid[5][6].isObstacle = True

    dists, path = search.a_star_search(
        wMap, (10.0, 380.0), (380.0, 10.0), search.euclidean)
    root = Tk()
    simulation = MapPath(root, wMap, path)
    simulation.updateGrid()
    root.mainloop()
