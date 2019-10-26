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

    def push(val):
        heapq.heappush(self._data, (key(val), val))

    """
    pops min cost element from heap
    """
    def pop():
        heapq.heappop(self._data)[1]

    """
    empties the heap
    """
    def clear():
        self._data = []


class Grid:
    '''
    Constructor for Grid: Initialize a matrix with size of rows and colums. The
    matrix is a 2d array collections of Tile objects.
    '''
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.matrix = [[Tile(x, y, None, True) for y in range(columns)] for x in range(rows)]
        self.explored = []
        # self.obstacles = []

    # Convert individual obstacle objects into a list
    def ListOfObstacles(self, tile_list):
        obstacles = []
        for tile in tile_list:
            if(not tile.isEmpty):
                # raise Exception('Can only add tile with an obstacle')
                obstacles.append(tile)

    # A* searching algortihm
    def a_star_search(graph, start, goal):

        raise Exception("Not implemented")



class Tile:
    '''
    The class Tile carries the information of position of each tile in the matrix.
    The position is represented by x, rows, and y, columns. It also contains info
    whether the tile is empty or not with boolean value and cost of reaching specific
    that tile. The cost is initialized to be None at first and then being updated
    to integer and every tile is initialized to be empty at first.
    '''
    def __init__(self, x, y, isEmpty):
        self.x = x
        self.y = y
        self.isEmpty = True
        self.G = 0
        self.H = 0

a = Grid(2, 3)
for i in range(a.rows):
    for j in range(a.columns):
        print(a.matrix[i][j], end = '')
    print('.')
