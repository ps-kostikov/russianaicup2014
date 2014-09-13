import math


def friction_factor():
    return 0.98


# 1-dimension model
def count_vn(v0, a, n):
    k = friction_factor()
    kn = k ** n
    return v0 * kn + (a * k) * (1 - kn) / (1. - k)


# 1-dimension model
def count_n(v0, a, vn):
    k = friction_factor()
    q = k / (1. - k)
    numerator = vn - a * q
    denominator = v0 - a * q

    if abs(denominator) < 0.00001:
        # print 'denominator is small ', denominator
        return None

    kn = numerator / denominator

    if (kn >= 1.) or (kn <= 0.):
        # print 'kn = ', kn
        return None

    return math.log(kn, k)


# 1-dimension model
def count_xn(x0, v0, a, n):
    k = friction_factor()
    kn = k ** n
    q = k / (1. - k)
    return x0 + v0 * q * (1. - kn) + n * a * q - a * q * q * (1. - kn)
