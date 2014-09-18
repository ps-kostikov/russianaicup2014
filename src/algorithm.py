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
