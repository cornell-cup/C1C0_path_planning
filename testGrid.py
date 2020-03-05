import unittest
from grid import *


class TestGridMethods(unittest.TestCase):

    def testTileInit(self):
        tile = Tile(5, 10)
        self.assertEqual(tile.x, 5)
        self.assertEqual(tile.y, 10)
        self.assertFalse(tile.isObstacle)

    def testHeapInit(self):
        heap = TileHeap()
        self.assertEqual(heap.data, [])
        self.assertEqual(heap.cost_map, {})
        self.assertEqual(heap.idx_map, {})

    def testPushPop(self):
        heap = TileHeap()
        tile0 = Tile(1, 1, isObstacle=False)
        tile1 = Tile(2, 2, isObstacle=False)
        tile2 = Tile(3, 3, isObstacle=False)
        tile3 = Tile(3, 3, isObstacle=True)
        def dist(x, y): return x**2 + y**2

        # two tiles have distinct cost
        heap.push(tile0, dist(tile0.x, tile0.y), 1)
        heap.push(tile1, dist(tile1.x, tile1.y), 1)
        self.assertEqual(heap.data, [tile0, tile1])
        self.assertEqual(heap.cost_map[tile0][0], 2)
        self.assertEqual(heap.cost_map[tile1][0], 8)
        self.assertEqual(heap.idx_map[tile0], 0)
        self.assertEqual(heap.idx_map[tile1], 1)

        heap.pop()
        self.assertEqual(heap.data, [tile1])
        heap.pop()
        self.assertEqual(heap.isEmpty(), True)
        self.assertEqual(heap.pop(), None)

        # two tiles have the same cost
        heap.push(tile2, dist(tile2.x, tile2.y), 1)
        heap.push(tile3, dist(tile3.x, tile3.y), 1)
        self.assertEqual(heap.data, [tile2, tile3])
        self.assertEqual(heap.cost_map[tile2][0], 18)
        self.assertEqual(heap.cost_map[tile3][0], 18)
        self.assertEqual(heap.idx_map[tile2], 0)
        self.assertEqual(heap.idx_map[tile3], 1)
        t3, cost3 = heap.pop()
        # the heap break ties basing on time that the elt enter the heap
        self.assertEqual(t3.isObstacle, False)
        self.assertEqual(heap.data, [tile3])
        heap.pop()
        heap.pop()

        self.assertEqual(heap.isEmpty(), True)
        # add tiles in a largest to smallest cost order
        heap.push(tile2, dist(tile2.x, tile2.y), 1)
        heap.push(tile1, dist(tile1.x, tile1.y), 1)
        heap.push(tile0, dist(tile0.x, tile0.y), 1)
        self.assertEqual(tile0, heap.pop()[0])
        self.assertEqual(tile1, heap.pop()[0])
        self.assertEqual(tile2, heap.pop()[0])
        self.assertEqual(heap.pop(), None)


if __name__ == '__main__':
    unittest.main()
