import grid
import search
import tkinter as tk
import time
import datetime
import random
import math

import Consts
import GenerateSensorData


class SquareObstacles():
    def __init__(self, coords, height, width):
        """A class to help create moving squares

        Arguments:
        coords -- The position of the obstacle (x, y)
        height -- height of square obstacle
        wdith --- width of square obstacle

        FIELDS:
        position {tile} -- (x, y) of the bottom left corner of the square obstacle
        height {int} -- height of square obstacle
        width {int} -- width of square obstacle
        """
        self.position = coords
        self.height = height
        self.width = width

    def pos(self):
        self.position