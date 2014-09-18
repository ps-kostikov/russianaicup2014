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

    def test_point_in_convex_polygon(self):
        polygon = [
            geometry.Point(0, 0),
            geometry.Point(1, 0),
            geometry.Point(1, 1),
            geometry.Point(0, 1),
        ]
        self.assertTrue(geometry.point_in_convex_polygon(
            geometry.Point(0.5, 0.5),
            polygon
        ))
        self.assertFalse(geometry.point_in_convex_polygon(
            geometry.Point(1.5, 0.5),
            polygon
        ))
        self.assertFalse(geometry.point_in_convex_polygon(
            geometry.Point(1.00001, 0.00001),
            polygon
        ))
        self.assertTrue(geometry.point_in_convex_polygon(
            geometry.Point(0.99999, 0.00001),
            polygon
        ))

if __name__ == '__main__':
    unittest.main()
