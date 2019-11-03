

class Heap:
    def __init__(self, comparator = None, isMinHeap):
        self.KV = [] # list of (tile, key) tuples
        self.mappings = {} # elts -> position in heap
        self.isMinHeap = isMinHeap
        self.size = size
        if not self.comparator:
            self.comparator = lambda x: x
        else:
            self.comparator = comparator

    # Constructor for tiles
    def __element__(self, key, value):
        self.key = key
        self.val = value
    '''
    If a value with key k1 should be above a value with key
        k2 in the heap, return 1.
    If key k1 and key k2 are the same, return 0.
    If a value with key k1 should be below a value with key
        k2 in the heap, return -1.
    This is based on what kind of a heap this is,
    E.g. a min-heap, the value with the smalllest key is in the root.
    E.g. a max-heap, the value with the largest key is in the root.
    '''
    def comparator(k1, k2):
        if k1 == k2: return 0
        if isMinHeap:
            if k1 < k2:
                return 1
            else:
                return -1
        else:
            if k1 > k2:
                return 1
            else:
                return -1

    def compareTo(m, n):
        return comparator(KV[m].key, KV[n].key)

    def swap(self, index1, index2):
        assert 0 <= index1 < size and 0 <= index2 < size
        temp = KV[index1]
        mappings.update(KV[index2].val = index1)
        mappings.update(temp.val = index2)
        KV[index1] = KV[index2]
        KV[index2] = temp

    def size():
        return size

    def mem(self, val):
        return val in self.mappings

    '''
    If KV[n] doesn't exist or has no child, return n.
        If KV[n] has one child, return its index.
        If KV[n] has two children with the same priority, return the
            index of the right one.
        If KV[n] has two children with different priorities return the
            index of the one that must appear above the other in a heap.
    '''
    def upperChild(n):
        if n >= size || 2*n + 1 >= size:
            return n
        if 2*n + 2 == size(self):
            return 2*n + 1
        if compareTo(2*n+1, 2*n+2) == 0:
            return 2*n + 2
        if compareTo(2*n+1, 2*n+2) == 1:
            return 2*n + 1
        return 2*n + 2

   '''
   Bubble KV[k] up the heap to its right place.
     Precondition: 0 <= k < size and
     The class invariant is true, except perhaps
     that KV[k] belongs above its parent (if k > 0)
     in the heap, not below it.
   '''
    def bubble_up(k):
        # TODO
        assert 0 <= k < size
        p = (k - 1) / 2
        while k > 0 &&  compareTo(KV[k].key, KV[p].key) > 0:
            swap(k, p)
            k = p
            p = ( k-1 ) / 2

    '''
    Bubble KV[k] down in heap until it finds the right place.
        If there is a choice to bubble down to both the left and
        right children (because their priorities are equal), choose
        the right child.
        Precondition: 0 <= k < size   and
                 Class invariant is true except that perhaps
                 KV[k] belongs below one or both of its children.
    '''
    def bubble_down(k):
        assert 0 <= k < size
        child = upperChild(k)
        while c < size && compareTo(k, c) < 0:
            swap(k, c)
            k = c
            c = upperChild(k)

    '''
    If this is a min-heap, return the heap value with lowest priority.
    If this is a max-heap, return the heap value with highest priority
    Do not change the heap. This operation takes constant time.
    Throw a NoSuchElementException if the heap is empty.
    '''
    def peek():
        if len(KV) == 0:
            raise NoSuchElementException
        else:
            return KV[0].val

    '''

    '''
    def push(value, key):
        # # TODO:
        KV[size] = element(value, key)
        mappings[value] = size
        size = size + 1
        bubble_up(size - 1)

    '''
    If this is a min-heap, remove and return heap value with smallest key.
       If this is a max-heap, remove and return heap value with largest key.
       The expected time is logarithmic and the worst-case time is linear
       in the size of the heap.
       Throw a NoSuchElementException if the heap is empty.
    '''
    def poll():
        if size == 0:
            raise NoSuchElementException
        remove = KV[0]
        swap(0, size - 1)
        del mappings[KV[size - 1].val]
        size = size - 1
        if size > 0:
            bubble_down(0)
        return remove.val


    '''
    Change the key of value v to new_key.
       The expected time is logarithmic and the worst-case time is linear
       in the size of the heap.
       Throw an IllegalArgumentException if v is not in the heap. */
    '''
    def update_key(value, new_key):
        index = mappings[value]
        KV[index].key = new_key
        bubble_up(index)
        bubble_down(index)


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

    def manhattan_distance(self, current_tile, end_tile):
        return abs(current_tile.x - end_tile.x) + abs(current_tile.y - end_tile.y)

    # A* searching algortihm
    def a_star_search(self, graph, start, goal):

        # heap -> open set ordered on cost
        heap = Heap(lambda tile: tile.G + tile.H, [start])

        # Initialize both open_set and closed_set
        # set -> open set
        open_set = {start: 0}
        # set -> closed set
        closed_set = set()

        # add start to heap G = 0, H = estimate to goal
        start.H = self.manhattan_distance(start, goal)
        open_set.add(start)


        # while heap is not empty
            # check if top of heap is goal
            # if not, add to closed set, get empty neighbors and calculate cost and heuristic
            # if neighbor in open set check if cost is less, if it is, update cost of successor and parent tile
            # if in closed set and cost is less, put closed set node back on open set and update parent (unsure)
            while not heap.isEmpty():
                top_elt = heap.pop()
                open_set.remove(top_elt)
                closed_set.add(top_elt)

                # if the top element is goal, stop the searching algorithm
                if top_elt == goal:
                    break

                # get a list of empty neighbor tiles
                neighbors = []
                cur_x = top_elt.x
                cur_y = top_elt.y

                next_tiles = [(cur_x - 1, cur_y), (cur_x + 1, cur_y), (cur_x, cur_y - 1), (cur_x, cur_y + 1)]
                for x, y in next_tiles:
                    if(0 <= x < Grid.rows and 0 <= y < Grid.columns and Grid[x][y].isEmpty and Grid[x][y] not in closed_set):
                        neighbors.append(Grid[x][y])

                # update the cost of successor and parent tile if neighbor
                # node is in open set
                for node in neighbors:
                    if node in open_set:
                        if top_elt.G + 1 < node.G:
                            node.G = top_elt.G + 1
                            node.parent = top_elt
                    else:
                        node.G = top_elt.G + 1
                        node.H = self.manhattan_distance(node, goal)
                        node.parent = top_elt
                        open_set.add(node)
                        heap.push(node)




        # fail if get to here here

    #Returns the path as a list of (x,y) coordinates, includes the tile itself
    def get_path(tile):
        path = []
        current_tile = tile
        while(current_tile is not None):
            path.append((current_tile.x, current_tile.y))
            current_tile = current_tile.parent
        return path

class Tile:
    '''
    The class Tile carries the information of position of each tile in the matrix.
    The position is represented by x, rows, and y, columns. It also contains info
    whether the tile is empty or not with boolean value and cost of reaching specific
    that tile. The cost is initialized to be None at first and then being updated
    to integer and every tile is initialized to be empty at first.
    '''
    def __init__(self, x, y, isEmpty = True, parent = None):
        # add parent tile field
        self.x = x
        self.y = y
        self.isEmpty = isEmpty
        self.parent = parent
        self.G = 0 # distance between the start node and the current node
        self.H = 0 # heuristic — estimated distance from the current node to the end node
        # F = G + H
        # self.F = 0 # total cost of the node

a = Grid(2, 3)
for i in range(a.rows):
    for j in range(a.columns):
        print(a.matrix[i][j], end = '')
    print('.')

# driver function
if __name__ == '__main__':
    main()
