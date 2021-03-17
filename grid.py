import math
from Tile import *

class Grid:
    def __init__(self, num_rows, num_cols, tile_length):
        """
        Initialize a grid of tiles with [num_rows] rows and [num_cols] cols, with
        each tile having length [tile_length]. The origin of the grid is the top left
        corner, with +x pointing to the right and +y pointing down.

        assumes: [num_rows] is even
        """
        # self.grid = [[Tile((tile_length/2) + (x * tile_length), (tile_length/2) + (y * tile_length), x, num_rows-y-1)
        #               for x in range(num_cols)] for y in range(num_rows-1, -1, -1)]
        self.grid = [[Tile((tile_length / 2) + (x * tile_length), (tile_length / 2) + (y * tile_length), y, x)
                      for x in range(num_cols)] for y in range(num_rows)]  # upper left origin
        self.tileLength = tile_length
        self.num_rows = num_rows
        self.num_cols = num_cols
        # TODO change center pos

    # def updateGrid(self, x, y, sensorDataTop, sensorDataBot, lidarData, path):
    #     """
    #     Marks tiles of grid as occuppied using IR sensor data [sensorData] measured
    #     from x position [x] and y position [y].
    #     """
    #     # returner is a variable to keep track of whether
    #     # A-star needs to be re-run
    #     returner = False
    #     for i in range(len(sensorDataTop)):
    #         angle = ir_mappings_top[i]
    #         distance = sensorDataTop[i]
    #         if distance != -1:
    #             x_obst = x + robot_radius + distance * math.cos(angle)
    #             # y_obst = y + radius + distance * math.sin(angle)
    #             y_obst = y + robot_radius - distance * \
    #                      math.sin(angle)  # upper left origin
    #             col = self._get_idx(x_obst, False)
    #             row = self._get_idx(y_obst, True)
    #             if (self.grid[row][col].isObstacle == False):
    #                 if row > len(self.grid) or col > len(self.grid[0]):
    #                     # TODO handle offgrid case
    #                     return
    #                 if (self.grid[row][col] in path):
    #                     returner = True
    #                 self.grid[row][col].isObstacle = True
    #                 if (self.bloat_tile(row, col, path) == True):
    #                     returner = True
    #
    #     for i in range(len(sensorDataBot)):
    #         angle = ir_mappings_bot[i]
    #         distance = sensorDataBot[i]
    #         if distance != -1:
    #             x_obst = x + robot_radius + distance * math.cos(angle)
    #             # y_obst = y + radius + distance * math.sin(angle)
    #             y_obst = y + robot_radius - distance * \
    #                      math.sin(angle)  # upper left origin
    #             col = self._get_idx(x_obst, False)
    #             row = self._get_idx(y_obst, True)
    #             if (self.grid[row][col].isObstacle == False):
    #                 if row > len(self.grid) or col > len(self.grid[0]):
    #                     # TODO handle offgrid case
    #                     return
    #                 if (self.grid[row][col] in path):
    #                     returner = True
    #                 self.grid[row][col].isObstacle = True
    #                 if (self.bloat_tile(row, col, robot_radius) == True):
    #                     returner = True
    #
    #     for i in lidarData:
    #         angle = i[0]
    #         distance = i[1]
    #         if distance != -1:
    #             x_obst = x + robot_radius + distance * math.cos(angle)
    #             # y_obst = y + radius + distance * math.sin(angle)
    #             y_obst = y + robot_radius - distance * \
    #                      math.sin(angle)  # upper left origin
    #             col = self._get_idx(x_obst, False)
    #             row = self._get_idx(y_obst, True)
    #             if (self.grid[row][col].isObstacle == False):
    #                 if row > len(self.grid) or col > len(self.grid[0]):
    #                     # TODO handle offgrid case
    #                     return
    #                 if (self.grid[row][col] in path):
    #                     returner = True
    #                 self.grid[row][col].isObstacle = True
    #                 if (self.bloat_tile(row, col, robot_radius) == True):
    #                     returner = True
    #         return returner

    def update_grid(self, x, y, sensor_state, radius, bloat_factor, path_set = set()):
        lidar_conflict = self.update_grid_tup_data(x, y, sensor_state.lidar, radius, bloat_factor, path_set)
        terabee_bot_conflict = self.update_grid_terabee(x, y, sensor_state.terabee_bot, radius, bloat_factor, path_set)
        terabee_mid_conflict = self.update_grid_terabee(x, y, sensor_state.terabee_mid, radius, bloat_factor, path_set)
        terabee_top_conflict = self.update_grid_terabee(x, y, sensor_state.terabee_top, radius, bloat_factor, path_set)
        return lidar_conflict or terabee_bot_conflict or terabee_mid_conflict or terabee_top_conflict

    def update_grid_terabee(self, x, y, terabee_data, terabee_dict, radius, bloat_factor, path_set):
        tuple_data = []
        for i in range(len(terabee_data)):
            tuple_data.append((terabee_dict[i], terabee_data[i]))

        return self.update_grid_tup_data(x, y, tuple_data, radius, bloat_factor, path_set)

    def update_grid_tup_data(self, x, y, tup_data, radius, bloat_factor, path_set):
        """updates the grid based on the lidarData passed in

        Arguments:
            x {[int]} -- [x coordinate of current location]
            y {[int]} -- [y coordinate of current location]
            lidarData {[(int*int) list]} -- [list of lidar data points where
            every of the entry is of the form (angle, distance)]
            path {[tile list]} -- [a path that a* star has outputted]

        Returns:
            [boolean] -- [True if the update based on the lidar interferes with 
            the path]
        """
        returner = False
        for i in tup_data:
            ang_deg = i[0]
            ang_rad = ang_deg * math.pi / 180
            distance = i[1]
            if distance != -1:
                x_obst = distance * math.cos(ang_rad)
                y_obst = distance * math.sin(ang_rad)  # upper left origin
                col = self._get_idx(x + x_obst, False)
                row = self._get_idx(y + y_obst, True)
                if col is not None and row is not None:
                    if self.grid[row][col] in path_set:
                        returner = True
                    self.grid[row][col].is_obstacle = True
                    self.grid[row][col].is_bloated = False
                    if self.bloat_tile(row, col, radius, bloat_factor, path_set):
                        returner = True
        return returner

    def bloat_tile(self, row, col, radius, bloat_factor, path_set=set()):
        """
        Bloats tiles in grid around the obstacle with index [row][col] within radius [radius].
        Going off grid, could final tile get bloated?
        TODO EDGE CASES
        """
        bloat_radius = radius * bloat_factor
        index_radius_inner = int(bloat_radius / self.tileLength) + 1
        index_rad_outer = index_radius_inner + 2

        lower_row = int(max(0, row - index_rad_outer))
        lower_col = int(max(0, col - index_rad_outer))
        upper_row = int(min(row + index_rad_outer, self.num_rows))
        upper_col = int(min(col + index_rad_outer, self.num_cols))
        returner = False
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.grid[i][j]
                y_dist = abs(i - row)
                x_dist = abs(j - col)
                dist = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                # print("dist: " + str(dist))
                if dist < index_radius_inner:
                    if not curr_tile.is_obstacle:
                        curr_tile.is_obstacle = True
                        curr_tile.is_bloated = True
                        if curr_tile in path_set:
                            returner = True
        return returner

    def _get_idx(self, coord, is_y):
        """
        Gets index of tile in grid according to coordinate [coord]. [coord] is assumed
        to be a y coordinate if [is_y] is True, else [coord] is assumed to be an x coordinate
        returns None if coord isn't on the grid.
        """
        if is_y:
            if coord < 0 or coord > len(self.grid) * self.tileLength:
                # TODO handle off grid case
                return None
        else:
            if coord < 0 or coord > len(self.grid[0]) * self.tileLength:
                # TODO handle off grid case
                return None

        coord -= (self.tileLength / 2)
        if (-self.tileLength / 2) < coord < 0:
            return 0

        else:
            low_estimate = int(coord // self.tileLength)
            offset = coord % self.tileLength
            ret = low_estimate + \
                  1 if offset > (self.tileLength / 2) else low_estimate
            return ret
            # if is_y:
            #     return (len(self.grid) - 1) - ret
            # else:
            #     return ret

    def get_tile(self, coords):
        """
        returns the tile at (x,y) coordinates [coords]. If [coords] is outside the
        grid returns None
        """
        col = self._get_idx(coords[0], False)
        row = self._get_idx(coords[1], True)
        if col is None or row is None:
            return

        return self.grid[row][col]

    def get_neighbors(self, tile):
        """
        Returns a list of the free tiles neighboring [tile] in grid
        """
        col = self._get_idx(tile.x, False)
        row = self._get_idx(tile.y, True)
        res = []
        if col is None or row is None:
            return res

        options = [(col - 1, row), (col + 1, row), (col, row + 1), (col, row - 1)]
        for icol, irow in options:
            if not (0 <= icol < len(self.grid[0])) or not (0 <= irow < len(self.grid)):
                continue
            if self.grid[irow][icol].is_obstacle:
                continue
            res.append(self.grid[irow][icol])

        return res
