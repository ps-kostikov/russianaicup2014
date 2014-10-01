# -*- coding: utf-8 -*-

import math
import copy

import shortcuts
import geometry
import algorithm
import environment


class UnitShadow:
    def __init__(self, x, y, speed_x, speed_y, angle):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.angle = angle


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


def next_puck_position(env, puck=None, tick=1):
    if puck is None:
        puck = env.world.puck
    return UnitShadow(
        count_xn(puck.x, puck.speed_x, 0, tick, k=puck_friction_factor()),
        count_xn(puck.y, puck.speed_y, 0, tick, k=puck_friction_factor()),
        count_vn(puck.speed_x, 0, tick, k=puck_friction_factor()),
        count_vn(puck.speed_y, 0, tick, k=puck_friction_factor()),
        puck.angle
    )


def next_hockeyist_position(env, hockeyist, tick):
    return UnitShadow(
        count_xn(hockeyist.x, hockeyist.speed_x, 0, tick, k=friction_factor()),
        count_xn(hockeyist.y, hockeyist.speed_y, 0, tick, k=friction_factor()),
        count_vn(hockeyist.speed_x, 0, tick, k=friction_factor()),
        count_vn(hockeyist.speed_y, 0, tick, k=friction_factor()),
        hockeyist.angle
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

    return UnitShadow(next_goalie_x, next_goalie_y, 0., 0., goalie.angle)


def goalie_can_save_straight(env, puck=None, player=None, goalie=None):
    if puck is None:
        puck = env.world.puck
    if player is None:
        player = shortcuts.opponent_player(env)
    if goalie is None:
        goalie = shortcuts.goalie(env, player)

    goal_interval = shortcuts.goal_interval(env, player)

    intersection = geometry.ray_interval_intersection(
        puck.x, puck.y, puck.speed_x, puck.speed_y,
        goal_interval[0].x, goal_interval[0].y, goal_interval[1].x, goal_interval[1].y)

    # шайба не летит в ворота
    if intersection is None:
        return True

    if goalie is None:
        return False

    old_puck = puck
    old_goalie = goalie
    for i in range(50):
        next_puck = next_puck_position(env, old_puck)
        next_goalie = next_goalie_position(env, old_goalie, old_puck)
        # print 'next_puck', next_puck.x, next_puck.y
        # print 'next_goalie', next_goalie.x, next_goalie.y

        # HARDCODE
        if geometry.distance(next_puck, next_goalie) <= 50:
            return True

        if shortcuts.im_left(env):
            if next_puck.x > shortcuts.opponent_player(env).net_front:
                return False
        else:
            if next_puck.x < shortcuts.opponent_player(env).net_front:
                return False

        old_puck = next_puck
        old_goalie = next_goalie

    return True


def copy_env(env):
    n_world = copy.copy(env.world)
    n_world.puck = copy.copy(env.world.puck)
    n_world.hockeyists = [
        copy.copy(h)
        for h in env.world.hockeyists
    ]
    n_me = copy.copy(env.me)
    return environment.Environment(n_me, n_world, env.game, env.move)


def count_free_motion_next_tick(env):
    new_env = copy_env(env)

    def update_puck(new_puck, puck):
        new_puck.x = count_xn(puck.x, puck.speed_x, 0, 1, k=puck_friction_factor())
        new_puck.y = count_xn(puck.y, puck.speed_y, 0, 1, k=puck_friction_factor())
        new_puck.speed_x = count_vn(puck.speed_x, 0, 1, k=puck_friction_factor())
        new_puck.speed_y = count_vn(puck.speed_y, 0, 1, k=puck_friction_factor())

    def update_hockeyist(new_h, h):
        new_h.x = count_xn(h.x, h.speed_x, 0, 1, k=friction_factor())
        new_h.y = count_xn(h.y, h.speed_y, 0, 1, k=friction_factor())
        new_h.speed_x = count_vn(h.speed_x, 0, 1, k=friction_factor())
        new_h.speed_y = count_vn(h.speed_y, 0, 1, k=friction_factor())

    update_puck(new_env.world.puck, env.world.puck)

    for h in shortcuts.my_field_hockeyists(env) + shortcuts.opponent_field_hockeyists(env):
        new_h = filter(
            lambda nh: nh.id == h.id,
            new_env.world.hockeyists
        )[0]
        update_hockeyist(new_h, h)
    return new_env


def count_free_motion(env, tick_number):
    '''
    Возвращает {tick: env}
    '''
    res = {}
    old_env = env
    for tick in range(1, tick_number + 1):
        new_env = count_free_motion_next_tick(old_env)
        res[tick] = new_env
        old_env = new_env
    return res
