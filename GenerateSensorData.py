import grid
import math
from Consts import *


class GenerateSensorData():
    def __init__(self, Grid):
        """[A class to help generate sensor data based on a grid, and a location
        within the grid]

        Arguments:
        grid {Grid} -- [A grid object used to figure out where ]
        """
        self.grid = Grid.grid
        self.gridObj = Grid

    def generateLidar(self, degree_freq, row, col):
        """Generates Lidar data for the tile located at self.grid[row][col].
        generates a lidar data point measurement for every degree_freq around
        the robot

        Returns a list of tuples representing obstacles (obstacle deg, obstacle dist from robot)

        Arguments:
            row {int} -- The row that represents where the robot is at
            degree_freq {int} -- the angle between every lidar reading
            col {int} -- [the col that represents where the robot is at]
        """
        # Generates one lidar data point for every degree
        lidar_dists = []
        curr_tile = self.grid[row][col]
        for deg in range(0, 360, degree_freq):
            dist = tile_size / 2
            found_obj = False
            while (dist < vis_radius and found_obj == False):
                ang_rad = deg * math.pi / 180
                x_coor = curr_tile.x + math.cos(ang_rad) * dist
                y_coor = curr_tile.y + math.sin(ang_rad) * dist

                unknown_tile = self.gridObj.get_tile((x_coor, y_coor))

                if (not unknown_tile == None and unknown_tile.isObstacle and not unknown_tile.isBloated):
                    found_obj = True
                    lidar_dists.append((deg, dist))
                else:
                    dist = dist + tile_size / 2
        return lidar_dists
