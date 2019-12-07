<<<<<<< HEAD
import Search

my_heap = Search.Heap(True)

my_heap.push(2, 4)
=======
import unittest
import Search as S


class TestHeap(unittest.TestCase):
    def test_init(self):
        h = S.Heap(False)
        self.assertEqual(False, h.isMinHeap)
        self.assertEqual(0, h.size)
        self.assertEqual([], h.KV)
        self.assertEqual({}, h.mappings)

    def test_push(self):
        p = S.Heap(True)
        t0 = S.Tile(0, 0)
        p.push(t0, 10)
        self.assertEqual(1, p.size)
        self.assertEqual(t0, p.peek())
        self.assertEqual(0, p.mappings.get(t0))
        t1 = S.Tile(1, 5)
        p.push(t1, 3)
        # self.assertEqual(2, p.size)

    def test_mem(self):
        m = S.Heap(True)
        t0 = S.Tile(0, 0)
        t1 = S.Tile(1, 3)
        self.assertEqual(False, m.mem(t0))
        self.assertEqual(False, m.mem(t1))
        m.push(t0, 0)
        self.assertEqual(True, m.mem(t0))
        self.assertEqual(t0, m.peek())
        # m.poll()
        # self.assertEqual()


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHeap)
    # unittest.TextTestRunner(verbosity=2).run(suite)
>>>>>>> 1bad4ddc4b26602cc3bf331810619c23bc3f6b7a
