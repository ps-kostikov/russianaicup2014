import unittest

import geometry


class TestGeometry(unittest.TestCase):

    def test_interval_intersection(self):
        for args, answer in [
                ((0, 0, 0, 1, 0, 0, 1, 0), True),
                ((0, 0.5, 0, 1, 0.5, 0, 1, 0), False),
                ((0, 1, 1, 0, 0, 0, 1, 1), True),
                ((0, 1, 0.25, 0.75, 0, 0, 1, 1), False),
                ((0, 0, 1, 1, 0, 1, 1, 1.0004), False),
                ((0, 0, 1, 1, 0, 1, 1, 0.999), True),
                ((0, 0, 1, 1, 0, 1, 0.99, 1), False),
                ((0, 0, 0, 1, 1, 0, 1, 1), False),
        ]:
            self.assertEqual(
                geometry.are_intervals_intersect(*args),
                answer
            )


if __name__ == '__main__':
    unittest.main()
