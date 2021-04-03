import math
from Tile import *
from SensorState import *
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

    def update_grid(self, x, y, sensor_state: SensorState, radius, bloat_factor, path_set = set()):
        for i, sensor_data in enumerate(sensor_state.sensor_data):
            if i!= Tile.lidar:
                self.update_grid_terabee(x, y, sensor_data, terabee_dict_bot, radius, bloat_factor, path_set)
            else:
                self.update_grid_tup_data(x, y, sensor_data, terabee_dict_bot, radius, bloat_factor, path_set)

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
        sensor_non_tiles = self.find_non_objs(tup_data, x, y)

        for i in sensor_non_tiles:
            ang_deg = i[0]
            ang_rad = ang_deg * math.pi / 180
            distance = i[1]
            if distance != -1:
                x_nobst = distance * math.cos(ang_rad)
                y_nobst = distance * math.sin(ang_rad)
                col = self._get_idx(x + x_nobst, False)
                row = self._get_idx(y + y_nobst, True)
                if (not col == None and not row == None):
                    if (self.grid[row][col].obstacle_score != 0):
                        self.grid[row][col].obstacle_score -= 1
                        # print('LESS OBSTACLE')
                        if (self.grid[row][col].obstacle_score == 0):
                            # print('REMOVED OBSTACLE')
                            self.grid[row][col].is_obstacle = False
                            self.debloat_tile(row, col)
                            # check if it needs to be someone else's bloat tile

        returner = False
        for i in tup_data:
            # print(i)
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
                    self.grid[row][col].is_found = True
                    self.grid[row][col].is_obstacle = True
                    self.grid[row][col].is_bloated = False
                    self.grid[row][col].obstacle_score = obstacle_value
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

    def find_non_objs(self, tup_data, x, y):
        """Generates a list of tiles that a sensor decided are not obstacles.
        This is determined when the sensor gets an obstacle reading behind this obstacle

        Returns a list of tiles

        Arguments:
            tup_data {(int, int) list} -- list of sensor data
            x {int} -- robots x position
            y {int} -- robots y position
        """
        ## TODO
        return []
