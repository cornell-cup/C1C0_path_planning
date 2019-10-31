import heapq

#wrapper for python heapq
class HeapWrapper:
    """
    creates min-cost heap from [data] using comparator [key]
    cost is defined by comparator [key]
    assumes [key] is a function and [data] is an iterable
    """
    def __init__(self, key, data=[]):
        self.key = key
        if data:
            self._data = [(key(item), item) for item in data]
        heapq.heapify(self._data)

    def push(self, val):
        heapq.heappush(self._data, (self.key(val), val))

    """
    pops min cost element from heap
    """
    def pop(self):
        heapq.heappop(self._data)[1]

    """
    empties the heap
    """
    def clear(self):
        self._data = []


class Grid:
    '''
    Constructor for Grid: Initialize a matrix with size of rows and colums. The
    matrix is a 2d array collections of Tile objects.
    '''
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.matrix = [[Tile(x, y) for y in range(columns)] for x in range(rows)]
        self.explored = []
        # self.obstacles = []

    # Convert individual obstacle objects into a list
    def ListOfObstacles(self, tile_list):
        obstacles = []
        for tile in tile_list:
            if not tile.isEmpty:
                # raise Exception('Can only add tile with an obstacle')
                obstacles.append(tile)

    # A* searching algortihm
    def a_star_search(self, graph, start, goal):
        # heap -> open set ordered on cost
        # set -> open set
        # set -> closed set
        # add start to heap G = 0, H = estimate to goal
        # while heap is not empty
            # check if top of heap is goal
            # if not, add to closed set, get empty neighbors and calculate cost and heuristic
            # if neighbor in open set check if cost is less, if it is update cost of successor and parent tile
            # if in closed set and cost is less, put closed set node back on open set and update parent (unsure)

        # fail if get to here here

    #TODO get path funciton


        raise Exception("Not implemented")



class Tile:
    '''
    The class Tile carries the information of position of each tile in the matrix.
    The position is represented by x, rows, and y, columns. It also contains info
    whether the tile is empty or not with boolean value and cost of reaching specific
    that tile. The cost is initialized to be None at first and then being updated
    to integer and every tile is initialized to be empty at first.
    '''
    def __init__(self, x, y, isEmpty = True):
        # add parent tile field
        self.x = x
        self.y = y
        self.isEmpty = isEmpty
        self.G = 0
        self.H = 0

a = Grid(2, 3)
for i in range(a.rows):
    for j in range(a.columns):
        print(a.matrix[i][j], end = '')
    print('.')


