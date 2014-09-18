import unittest

import algorithm


class TestAlgorithm(unittest.TestCase):

    def test_binary_search(self):
        def f(x):
            return x ** 3

        eps = 1e-6
        self.assertAlmostEquals(algorithm.binary_search(-3, 3, f, eps), 0., delta=1e-2)


if __name__ == '__main__':
    unittest.main()
