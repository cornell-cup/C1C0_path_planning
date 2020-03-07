import unittest
import fa19.Search as S


class TestHeap(unittest.TestCase):
    def test_init(self):
        h = S.Heap(False)
        self.assertEqual(False, h.isMinHeap)
        self.assertEqual(0, h.size)
        self.assertEqual([], h.KV)
        self.assertEqual({}, h.mappings)

    def test_swap(self):
        h = S.Heap.(True)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHeap)
    # unittest.TextTestRunner(verbosity=2).run(suite)
