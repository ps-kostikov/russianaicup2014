# -*- coding: utf-8 -*-

import math

import shortcuts
import geometry
import algorithm


class UnitShadow:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y


def friction_factor():
    return 0.98


def puck_friction_factor():
    return 0.999


# 1-dimension model
def count_vn(v0, a, n, k=friction_factor()):
    '''
    считаем скорость через n тиков
    '''
    kn = k ** n
    return v0 * kn + (a * k) * (1 - kn) / (1. - k)


# 1-dimension model
def count_n(v0, a, vn, k=friction_factor()):
    '''
    считаем количество тиков при заданных v0 vn
    '''
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


def count_n_by_x(x0, v0, a, xn, k=friction_factor()):
    '''
    считаем количество тиков при заданных x0 v0 xn
    сложность log(количество тиков)
    '''
    def f(n):
        return xn - count_xn(x0, v0, a, n, k)

    # Это не совсем точно, может и доедем еще на v0
    if a * (xn - x0) < 0:
        return None

    return algorithm.binary_search(0, 8000, f, 0.01)


# 1-dimension model
def count_xn(x0, v0, a, n, k=friction_factor()):
    '''
    считаем позицию через n тиков при x0 v0
    '''
    kn = k ** n
    q = k / (1. - k)
    return x0 + v0 * q * (1. - kn) + n * a * q - a * q * q * (1. - kn)


def next_puck_position(env, puck=None):
    if puck is None:
        puck = env.world.puck
    return UnitShadow(
        count_xn(puck.x, puck.speed_x, 0, 1, k=puck_friction_factor()),
        count_xn(puck.y, puck.speed_y, 0, 1, k=puck_friction_factor()),
        count_vn(puck.speed_x, 0, 1, k=puck_friction_factor()),
        count_vn(puck.speed_y, 0, 1, k=puck_friction_factor())
    )


def next_goalie_position(env, goalie, puck=None):
    if puck is None:
        puck = env.world.puck

    next_goalie_x = goalie.x

    # HARDCODE
    goalie_radius = 30.
    min_goalie_y = env.game.goal_net_top + goalie_radius
    max_goalie_y = env.game.goal_net_top + env.game.goal_net_height - goalie_radius

    diff = puck.y - goalie.y
    if diff > 0:
        shift_y = min(diff, env.game.goalie_max_speed)
        next_goalie_y = min(max_goalie_y, goalie.y + shift_y)
    else:
        shift_y = max(diff, -env.game.goalie_max_speed)
        next_goalie_y = max(min_goalie_y, goalie.y + shift_y)

    return UnitShadow(next_goalie_x, next_goalie_y, 0., 0.)


def goalie_can_save(env, puck=None):
    '''
    Возвращаем True если вратарь не успевает отразить удар
    '''
    if puck is None:
        puck = env.world.puck
    goal_interval = shortcuts.opponent_goal_interval(env)
    goalie = shortcuts.opponent_goalie(env)
    my_goalie = shortcuts.my_goalie(env)

    intersection = geometry.ray_interval_intersection(
        puck.x, puck.y, puck.speed_x, puck.speed_y,
        goal_interval[0].x, goal_interval[0].y, goal_interval[1].x, goal_interval[1].y)

    # шайба не летит в ворота
    if intersection is None:
        # print 'intersection is None'
        return True

    if goalie is None or my_goalie is None:
        return False

    # distance = geometry.distance(intersection, puck)
    # puck_speed_abs = geometry.vector_abs(puck.speed_x, puck.speed_y)
    # print 'puck_speed_abs', puck_speed_abs
    # print 'distance', distance

    # Это неправильно, скорость уменьшается со временем
    related_speed_x = puck.speed_x
    if puck.speed_y > 0:
        # print 'puck.speed_y > 0'
        related_speed_y = puck.speed_y - env.game.goalie_max_speed
    else:
        related_speed_y = puck.speed_y + env.game.goalie_max_speed

    next_puck = puck
    # Условие надо сделать проще, на больше меньше по y, но надо учест направление удара
    while geometry.ray_interval_intersection_v2(
            geometry.Point(next_puck.x, next_puck.y),
            geometry.Point(next_puck.speed_x, next_puck.speed_y),
            goalie,
            my_goalie
        ) is not None:
        next_puck = next_puck_position(env, next_puck)

    # goalie_start_moving_point = geometry.ray_interval_intersection_v2(
    #     puck,
    #     geometry.Point(puck.speed_x, puck.speed_y),
    #     goalie,
    #     my_goalie
    # )
    # if goalie_start_moving_point is None:
    #     goalie_start_moving_point = puck

    # goalie_start_moving_point = geometry.Point(960.326538086, 394.877075195)
    goalie_start_moving_point = next_puck
    nearest_point = geometry.ray_point_nearest_point(
        goalie_start_moving_point,
        geometry.Point(related_speed_x, related_speed_y),
        goalie
    )
    # print 'puck', puck.x, puck.y
    # print 'goalie', goalie.x, goalie.y
    # print 'goalie_start_moving_point', goalie_start_moving_point.x, goalie_start_moving_point.y
    # print 'nearest_point', nearest_point

    distance_to_nearest_point = geometry.distance(
        goalie,
        nearest_point
    )
    # print 'distance_to_nearest_point', distance_to_nearest_point
    return distance_to_nearest_point <= goalie.radius + env.world.puck.radius


def goalie_can_save_straight(env, puck=None, goalie=None):
    if puck is None:
        puck = env.world.puck
    goal_interval = shortcuts.opponent_goal_interval(env)
    if goalie is None:
        goalie = shortcuts.opponent_goalie(env)
    my_goalie = shortcuts.my_goalie(env)

    intersection = geometry.ray_interval_intersection(
        puck.x, puck.y, puck.speed_x, puck.speed_y,
        goal_interval[0].x, goal_interval[0].y, goal_interval[1].x, goal_interval[1].y)

    # шайба не летит в ворота
    if intersection is None:
        return True

    if goalie is None or my_goalie is None:
        return False

    old_puck = puck
    old_goalie = goalie
    for i in range(50):
        next_puck = next_puck_position(env, old_puck)
        next_goalie = next_goalie_position(env, old_goalie, old_puck)
        # print 'next_puck', next_puck.x, next_puck.y
        # print 'next_goalie', next_goalie.x, next_goalie.y

        if shortcuts.im_left(env):
            if next_puck.x > shortcuts.opponent_player(env).net_front:
                return False
        else:
            if next_puck.x < shortcuts.opponent_player(env).net_front:
                return False
        # HARDCODE
        if geometry.distance(next_puck, next_goalie) <= 50:
            return True

        old_puck = next_puck
        old_goalie = next_goalie

    return True
