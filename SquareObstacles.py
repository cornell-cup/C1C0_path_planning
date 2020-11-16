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
    def __init__(self, x, y, height, width, velocity, counter):
        """A class to help create moving squares

        Arguments:
        x -- The x coordianate of the obstacle
        y -- The y coordinate of the obstacle
        height -- height of square obstacle
        width --- width of square obstacle
        velocity -- the velocity of obstacle
        counter -- keeps track of frames

        FIELDS:
        x {int} -- the x coordinate of the bottom of the square obstacle
        y {int} -- the y coordinate of the left of the square obstacle
        height {int} -- height of square obstacle
        width {int} -- width of square obstacle
        velocity -- the random velocity of the obstacle
        counter -- keeps track of the frames (only needed for velocities < 1 because the object will move after a
        a certain number of frames : i.e velocity of 1/2 means the obstacle will be 1 tile every 2 frames)
        """
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.velocity = velocity
        self.counter = counter

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, new_x):
        self.x = new_x

    def setY(self, new_y):
        self.y = new_y

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getVelocity(self):
        return self.velocity

    def getCounter(self):
        return self.counter

    def setCounter(self, count):
        self.counter = count

