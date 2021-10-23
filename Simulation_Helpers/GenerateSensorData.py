import math
from Constants.Consts import *


class GenerateSensorData():
    def __init__(self, Grid):
        """[A class to help generate sensor data based on a grid, and a location
        within the grid]

        Arguments:
        grid {Grid} -- [A grid object used to figure out where ]
        """
        self.grid = Grid.grid
        self.gridObj = Grid

    def generateLidar2(self, degree_freq, row, col):
        ans = {deg:3*vis_radius for deg in range(0, 360, degree_freq)}
        curr_tile = self.grid[row][col]
        counter = 0
        x_shift = -1*vis_radius
        while x_shift <= vis_radius:
            y_shift = -1*vis_radius
            while y_shift <= vis_radius:
                x_coor = curr_tile.x + x_shift
                y_coor = curr_tile.y + y_shift
                unknown_tile = self.gridObj.get_tile((x_coor, y_coor))
                if unknown_tile is not None and unknown_tile.is_obstacle and not unknown_tile.is_bloated:
                    angle = int(180/math.pi * math.atan2(y_shift, x_shift)/degree_freq) * degree_freq
                    angle = angle if angle >= 0 else angle + 360
                    ans[angle] = min(ans[angle], math.sqrt(y_shift**2 + x_shift**2))
                y_shift += tile_size
            x_shift += tile_size
        for key in list(ans.keys()).copy():
            if ans[key] > vis_radius:
                del ans[key]

        print()
        print(ans)
        # ans2 = self.generateLidar(degree_freq, row, col)
        # print(ans2)
        return [(key, ans[key]) for key in ans.keys()]

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
            while dist < vis_radius and not found_obj:
                # while_count += 1
                ang_rad = deg * math.pi / 180
                x_coor = curr_tile.x + math.cos(ang_rad) * dist
                y_coor = curr_tile.y + math.sin(ang_rad) * dist

                unknown_tile = self.gridObj.get_tile((x_coor, y_coor))

                if unknown_tile is not None and unknown_tile.is_obstacle and not unknown_tile.is_bloated:
                    found_obj = True
                    lidar_dists.append((deg, dist))
                else:
                    dist = dist + tile_size / 2
        # print("while count", while_count)
        return lidar_dists
