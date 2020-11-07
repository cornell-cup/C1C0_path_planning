import heapq
import math

# dict mapping position in IR sensor array to angular position on C1C0 (relative to front)
ir_mappings_top = {}
ir_mappings_bot = {}


class Tile:
    def __init__(self, x, y, row, col, isObstacle=False, isBloated=False, isKnown=False):
        """
        Initialize a tile centered at x coordinate [x] and y coordinate [y].
        If [isObstacle] is True, the tile is initialized as an obstacle, else Tile is
        marked as free space, [isObstacle] is False by default.
        """
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.isObstacle = isObstacle
        self.isBloated = isBloated


class TileHeap:
    def __init__(self):
        """
        Initializes an empty heap of tiles.
        """
        self.data = []
        self.cost_map = {}  # to keep track of each tiles cost + heuristic
        self.idx_map = {}  # to keep track of each tiles index in data

    def comparator(self, pos1, pos2):
        """
        given index [pos1] and index [pos2] of the heap, returns 0 if tile at
        [pos1] has same cost + heuristic as the tile at [pos2]; returns -1 if
        tile at [pos1] has greater cost + heuristic than tile at [pos2] and returns
        1 if tile at [pos1] has smaller cost + heuristic than tile at [pos2].
        """
        tile1 = self.data[pos1]
        tile2 = self.data[pos2]
        data1 = self.cost_map[tile1][0] + self.cost_map[tile1][1]
        data2 = self.cost_map[tile2][0] + self.cost_map[tile2][1]
        if data1 == data2:
            return 0
        elif data1 > data2:
            return -1
        else:
            return 1

    def push(self, elt, cost, heuristic):
        """
        Push tile [elt] on to the heap with cost [cost] and heuristic estimate
        [heuristic]

        assumes: [elt] is a Tile object, [cost] and [heuristic] are floats
        """
        if elt in self.idx_map:
            return None

        pos = len(self.data)
        self.idx_map[elt] = pos
        self.cost_map[elt] = [cost, heuristic]
        self.data.append(elt)
        self._bubble_up(pos)

    def pop(self):
        """
        Pop tile with minimum cost + heuristic from heap and return a tuple of tile
        and cost to get to the tile (in that order), returns None if heap is empty.
        """
        if self.isEmpty():
            return None

        elt = self.data[0]
        cost = self.cost_map[elt][0]
        del self.idx_map[elt]
        del self.cost_map[elt]
        if len(self.data) == 1:
            self.data = []
        else:
            last = self.data.pop()
            self.data[0] = last
            self.idx_map[last] = 0
            self._bubble_down(0)

        return (elt, cost)

    def _swap(self, pos1, pos2):
        """
        swap tile at [pos1] in heap with tile at [pos2] in heap.
        """
        elt1 = self.data[pos1]
        elt2 = self.data[pos2]
        self.idx_map[elt1], self.idx_map[elt2] = pos2, pos1
        self.data[pos1], self.data[pos2] = elt2, elt1

    def _bubble_up(self, pos):
        """
        helper function for [push] and [updatePriority]
        """
        parent = (pos - 1) // 2
        while pos > 0 and self.comparator(pos, parent) > 0:
            self._swap(pos, parent)
            pos = parent
            parent = (pos - 1) // 2

    def _biggerChild(self, pos):
        """
        helper function for [pop], returns the child of element at [pos] with the
        highest priority
        """
        c = 2 * pos + 2
        if c >= len(self.data) or self.comparator(c - 1, c) > 0:
            c = c - 1
        return c

    def _bubble_down(self, pos):
        """
        helper function for [pop] and [updatePriority]
        """
        child = self._biggerChild(pos)
        while (child < len(self.data) and self.comparator(pos, child) < 0):
            self._swap(pos, child)
            pos = child
            child = self._biggerChild(pos)

    def updatePriority(self, elt, new_cost):
        """
        updates tile [elt] in the heap with cost [new_cost].
        Assumes [elt] is already in the heap

        Note: [new_cost] should not include heuristic estimate
        """
        self.cost_map[elt][0] = new_cost
        pos = self.idx_map[elt]
        self._bubble_up(pos)
        self._bubble_down(pos)

    def isEmpty(self):
        """
        Returns True if heap is empty, else returns False
        """
        return False if self.data else True

    def mem(self, elt):
        """
        returns True if [elt] is in the heap, else returns False
        """
        return elt in self.idx_map

    def getCost(self, elt):
        """
        Returns the cost from start to tile [elt] if [elt] is in heap, else returns
        None
        """
        if not self.mem(elt):
            return
        return self.cost_map[elt][0]


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

    def updateGrid(self, x, y, sensorDataTop, sensorDataBot, lidarData, path):
        """
        Marks tiles of grid as occuppied using IR sensor data [sensorData] measured
        from x position [x] and y position [y].
        """
        # returner is a variable to keep track of whether
        # A-star needs to be re-run
        returner = False
        for i in range(len(sensorDataTop)):
            angle = ir_mappings_top[i]
            distance = sensorDataTop[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                # y_obst = y + radius + distance * math.sin(angle)
                y_obst = y + radius - distance * \
                         math.sin(angle)  # upper left origin
                col = self._get_idx(x_obst, False)
                row = self._get_idx(y_obst, True)
                if (self.grid[row][col].isObstacle == False):
                    if row > len(self.grid) or col > len(self.grid[0]):
                        # TODO handle offgrid case
                        return
                    if (self.grid[row][col] in path):
                        returner = True
                    self.grid[row][col].isObstacle = True
                    if (self.bloat_tile(row, col, path) == True):
                        returner = True

        for i in range(len(sensorDataBot)):
            angle = ir_mappings_bot[i]
            distance = sensorDataBot[i]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                # y_obst = y + radius + distance * math.sin(angle)
                y_obst = y + radius - distance * \
                         math.sin(angle)  # upper left origin
                col = self._get_idx(x_obst, False)
                row = self._get_idx(y_obst, True)
                if (self.grid[row][col].isObstacle == False):
                    if row > len(self.grid) or col > len(self.grid[0]):
                        # TODO handle offgrid case
                        return
                    if (self.grid[row][col] in path):
                        returner = True
                    self.grid[row][col].isObstacle = True
                    if (self.bloat_tile(row, col, radius) == True):
                        returner = True

        for i in lidarData:
            angle = i[0]
            distance = i[1]
            if distance != -1:
                x_obst = x + radius + distance * math.cos(angle)
                # y_obst = y + radius + distance * math.sin(angle)
                y_obst = y + radius - distance * \
                         math.sin(angle)  # upper left origin
                col = self._get_idx(x_obst, False)
                row = self._get_idx(y_obst, True)
                if (self.grid[row][col].isObstacle == False):
                    if row > len(self.grid) or col > len(self.grid[0]):
                        # TODO handle offgrid case
                        return
                    if (self.grid[row][col] in path):
                        returner = True
                    self.grid[row][col].isObstacle = True
                    if (self.bloat_tile(row, col, radius) == True):
                        returner = True
            return returner

    def updateGridLidar(self, x, y, lidarData, radius, bloat_factor, pathSet, fullGrid):
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
        for i in lidarData:
            ang_deg = i[0]
            ang_rad = ang_deg * math.pi / 180
            distance = i[1]
            if distance != -1:
                x_obst = distance * math.cos(ang_rad)
                y_obst = distance * math.sin(ang_rad)  # upper left origin
                col = self._get_idx(x + x_obst, False)
                row = self._get_idx(y + y_obst, True)
                if (not col == None and not row == None):
                    if (self.grid[row][col] in pathSet):
                        returner = True
                    self.grid[row][col].isFound = True
                    self.grid[row][col].isObstacle = True
                    self.grid[row][col].isBloated = False
                    if (self.bloat_tile(row, col, radius, bloat_factor, pathSet) == True):
                        returner = True
        return returner

    def bloat_tile(self, row, col, radius, bloat_factor, pathSet=set()):
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
        # print("lower radius: " + str(index_radius_inner) +
        #      " upper radius: " + str(index_rad_outer))
        # print("lower col: " + str(lower_col) + " upper row: " + str(upper_col))
        # print("lower row: " + str(lower_row) + " upper row: " + str(upper_row))
        # print("++++++++++++++++++++++++++++++++++++++++")
        returner = False
        for i in range(lower_row, upper_row):
            for j in range(lower_col, upper_col):
                curr_tile = self.grid[i][j]
                y_dist = abs(i - row)
                x_dist = abs(j - col)
                dist = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                # print("dist: " + str(dist))
                if (dist < index_radius_inner):
                    if (not curr_tile.isObstacle):
                        curr_tile.isObstacle = True
                        curr_tile.isBloated = True
                        if (curr_tile in pathSet):
                            returner = True
        return returner
        """
        returner = False
        bloated_radius = radius * bloatFactor
        lower_left_x = row - bloated_radius if row - bloated_radius >= 0 else 0
        lower_left_y = col - bloated_radius if col - bloated_radius >= 0 else 0
        upper_right_x = row + bloated_radius if row + \
            bloated_radius < self.num_rows else self.num_rows - 1
        upper_right_y = col + bloated_radius if col + \
            bloated_radius < self.num_cols else self.num_cols - 1
        for i in range(lower_left_x, upper_right_x + 1, 1):
            for j in range(lower_left_y, upper_right_y + 1, 1):
                if(self.grid[i][j] in path):
                    returner = True
                self.grid[i][j].isBloated = True
                self.grid[i][j].isObstacle = True
        return returner
        """

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
            if self.grid[irow][icol].isObstacle:
                continue
            res.append(self.grid[irow][icol])

        return res
