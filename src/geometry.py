# -*- coding: utf-8 -*-

'''
Functions related to geometry evaluations
'''

import math
import collections


Point = collections.namedtuple('Point', 'x y')
Polygon = collections.namedtuple('Polygon', 'points')


def rad_to_degree(rad):
    return (rad * 180.) / math.pi


def degree_to_rad(degree):
    return (degree * math.pi) / 180.


def intervals_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    a1 = x2 - x1
    a2 = y2 - y1
    b1 = x3 - x4
    b2 = y3 - y4
    c1 = x3 - x1
    c2 = y3 - y1
    d = float(a1 * b2 - a2 * b1)

    if abs(d) < 0.001:
        return None

    t = (c1 * b2 - c2 * b1) / d
    s = (c2 * a1 - c1 * a2) / d

    if 0 <= t <= 1 and 0 <= s <= 1:
        return Point(x2 * t + (1 - t) * x1, y2 * t + (1 - t) * y1)
    return None


def are_intervals_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    return intervals_intersection(x1, y1, x2, y2, x3, y3, x4, y4) is not None


def interval_interval_intersection(p1, p2, p3, p4):
    return intervals_intersection(
        p1.x, p1.y,
        p2.x, p2.y,
        p3.x, p3.y,
        p4.x, p4.y
    )


def ray_interval_intersection(x1, y1, vx2, vy2, x3, y3, x4, y4):
    vnorm = math.hypot(vx2, vy2)
    if vnorm < 0.00001:
        return None
    k = 8000. / vnorm
    x2 = x1 + k * vx2
    y2 = y1 + k * vy2
    return intervals_intersection(x1, y1, x2, y2, x3, y3, x4, y4)


def ray_interval_intersection_v2(p1, v2, p3, p4):
    return ray_interval_intersection(
        p1.x, p1.y,
        v2.x, v2.y,
        p3.x, p3.y,
        p4.x, p4.y
    )


def get_nearest_point(bx, by, ex, ey, px, py):
    if math.hypot(bx - px, by - py) < 0.0001:
        return Point(bx, by)
    if math.hypot(ex - px, ey - py) < 0.0001:
        return Point(ex, ey)
    ebx = bx - ex
    eby = by - ey
    l_eb = math.hypot(ebx, eby)

    nebx = ebx / l_eb
    neby = eby / l_eb

    epx = px - ex
    epy = py - ey

    l_ep = math.hypot(epx, epy)

    angle = get_angle(ebx, eby, epx, epy)

    nx = ex + nebx * math.cos(angle) * l_ep
    ny = ey + neby * math.cos(angle) * l_ep

    return Point(nx, ny)


def interval_point_nearest_point(ibegin, iend, point):
    if ray_ray_angle(ibegin, iend, point) >= degree_to_rad(90):
        return iend
    if ray_ray_angle(iend, ibegin, point) >= degree_to_rad(90):
        return ibegin
    return get_nearest_point(ibegin.x, ibegin.y, iend.x, iend.y, point.x, point.y)


def interval_point_distance(ibegin, iend, point):
    np = interval_point_nearest_point(ibegin, iend, point)
    return distance(np, point)


def ray_point_nearest_point(ray_begin, ray_vector, point):
    vnorm = math.hypot(ray_vector.x, ray_vector.y)
    if vnorm < 0.00001:
        return None
    k = 8000. / vnorm
    ray_end = Point(
        ray_begin.x + k * ray_vector.x,
        ray_begin.y + k * ray_vector.y
    )

    if ray_ray_angle(ray_end, ray_begin, point) > degree_to_rad(90):
        return ray_begin

    return interval_point_nearest_point(ray_begin, ray_end, point)


def ray_point_distance(ray_begin, ray_vector, point):
    return distance(
        point,
        ray_point_nearest_point(ray_begin, ray_vector, point)
    )


def get_angle(v1x, v1y, v2x, v2y):
    '''
    угол между векторами (от 0 до pi)
    '''
    l1 = math.hypot(v1x, v1y)
    l2 = math.hypot(v2x, v2y)
    prod = (v1x * v2x + v1y * v2y) / (l1 * l2)
    if prod < -1:
        prod = -1
    if prod > 1:
        prod = 1
    return math.acos(prod)


def ray_ray_angle(point1, point0, point2):
    '''
    угол между лучами (от 0 до pi)
    '''
    return get_angle(
        point1.x - point0.x,
        point1.y - point0.y,
        point2.x - point0.x,
        point2.y - point0.y
    )


def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def vector_abs(*args):
    if len(args) == 1:
        point = args[0]
        return math.hypot(point.x, point.y)
    elif len(args) == 2:
        x, y = args
        return math.hypot(x, y)


def diff(point_begin, point_end):
    return Point(
        point_end.x - point_begin.x,
        point_end.y - point_begin.y
    )


def point_plus_vector(point, angle, length):
    return Point(
        point.x + math.cos(angle) * length,
        point.y + math.sin(angle) * length
    )


def angle_vector(angle, length):
    return Point(
        math.cos(angle) * length,
        math.sin(angle) * length
    )


def polygon_intervals(polygon):
    next_points = [polygon.points[-1]] + polygon.points[:-1]
    return list(zip(polygon.points, next_points))


def point_in_convex_polygon(point, polygon):
    for p in polygon.points:
        if distance(point, p) < 0.00001:
            return True
    next_points = [polygon.points[-1]] + polygon.points[:-1]
    angle_sum = sum(
        ray_ray_angle(p1, point, p2)
        for p1, p2 in zip(polygon.points, next_points)
    )
    return abs(angle_sum - degree_to_rad(360)) < 0.0001


def convex_polygon_point_nearest_point(polygon, point):
    if point_in_convex_polygon(point, polygon):
        return point
    next_points = [polygon.points[-1]] + polygon.points[:-1]
    np_dist = []
    for p1, p2 in zip(polygon.points, next_points):
        np = interval_point_nearest_point(p1, p2, point)
        dist = distance(np, point)
        np_dist.append((np, dist))
    return min(np_dist, key=lambda x: x[1])[0]


def convex_polygon_point_distance(polygon, point):
    return distance(
        point,
        convex_polygon_point_nearest_point(polygon, point)
    )


def convex_polygons_nearest_point(polygons, point):
    nearest_points = [
        convex_polygon_point_nearest_point(polygon, point)
        for polygon in polygons
    ]
    return min(
        nearest_points,
        key=lambda np: distance(np, point))


def convex_polygons_point_distance(polygons, point):
    return distance(
        convex_polygons_nearest_point(polygons, point),
        point
    )
