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

    def test_swap(self):
        h = S.Heap(True)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHeap)
    # unittest.TextTestRunner(verbosity=2).run(suite)
>>>>>>> 1bad4ddc4b26602cc3bf331810619c23bc3f6b7a
