import geometry


def binary_search(v_min, v_max, func, eps):
    def sign(x):
        return 1 if x > 0 else -1

    if v_min > v_max:
        return None

    f_min = func(v_min)
    f_max = func(v_max)

    if sign(f_max) == sign(f_min):
        return None

    v_middle = (v_min + v_max) / 2.
    if abs(f_max - f_min) < eps:
        return v_middle

    f_middle = func(v_middle)
    if sign(f_middle) == sign(f_max):
        return binary_search(v_min, v_middle, func, eps)
    else:
        return binary_search(v_middle, v_max, func, eps)


def best_point_in_interval(p1, p2, f):
    n = 10
    dx = (p2.x - p1.x) / n
    dy = (p2.y - p1.y) / n
    points = [
        geometry.Point(
            p1.x + dx * i,
            p1.y + dy * i)
        for i in range(n + 1)]
    return max(
        points,
        key=lambda p: f(p)
    )


def best_point_for_polynom(polynom, f):
    best_points = [
        best_point_in_interval(i[0], i[1], f)
        for i in geometry.polygon_intervals(polynom)
    ]
    return max(
        best_points,
        key=lambda bp: f(bp))


def best_point_for_polynoms(polynoms, f):
    best_points = [
        best_point_for_polynom(p, f)
        for p in polynoms
    ]
    return max(
        best_points,
        key=lambda bp: f(bp))
