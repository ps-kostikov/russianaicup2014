# -*- coding: utf-8 -*-

from model.HockeyistType import HockeyistType
from model.HockeyistState import HockeyistState

import geometry

import math


def my_player(env):
    return env.world.get_my_player()


def opponent_player(env):
    return env.world.get_opponent_player()


def goal_interval(env, player):
    return [
        geometry.Point(player.net_front, player.net_top),
        geometry.Point(player.net_front, player.net_bottom),
    ]


def opponent_goal_interval(env):
    return goal_interval(env, opponent_player(env))


def net_front_center(env, player):
    return geometry.Point(
        player.net_front,
        (player.net_top + player.net_bottom) / 2.
    )


def goalie(env, player):
    for h in env.world.hockeyists:
        if h.player_id == player.id and h.type == HockeyistType.GOALIE:
            return h
    return None


def my_goalie(env):
    return goalie(env, my_player(env))


# HARDCODE
def goalie_radius():
    return 30.


def opponent_goalie(env):
    return goalie(env, opponent_player(env))


def field_center(env):
    x = (env.game.rink_left + env.game.rink_right) / 2.
    y = (env.game.rink_top + env.game.rink_bottom) / 2.
    return geometry.Point(x, y)


def rink_center(env):
    return field_center(env)


def max_tick(env):
    return env.game.overtime_tick_count + env.game.tick_count


def player_left_sign(env, player):
    return 1. if player.net_back < rink_center(env).x else -1.


def player_left(env, player):
    return player_left_sign(env, player) > 0


def im_left_sign(env):
    return player_left_sign(env, my_player(env))


def im_left(env):
    return player_left(env, my_player(env))


def my_field_hockeyists(env):
    return filter(
        lambda h: h.teammate and h.type != HockeyistType.GOALIE and h.state != HockeyistState.RESTING,
        env.world.hockeyists)


def opponent_field_hockeyists(env):
    return filter(
        lambda h: not h.teammate and h.type != HockeyistType.GOALIE and h.state != HockeyistState.RESTING,
        env.world.hockeyists)


def field_hockeyists(env):
    return filter(
        lambda h: h.type != HockeyistType.GOALIE and h.state != HockeyistState.RESTING,
        env.world.hockeyists)


def nearest_unit(units, target):
    return min(
        *units,
        key=lambda u: geometry.distance(u, target)
    )


def hockeyist_can_take_puck(env, hockeyist):
    distance = geometry.distance(hockeyist, env.world.puck)
    angle = geometry.unit_angle_to(hockeyist, env.world.puck)

    return distance <= env.game.stick_length and abs(angle) <= env.game.stick_sector / 2.


def can_take_puck(env):
    return hockeyist_can_take_puck(env, env.me)


def hockeyist_can_strike_unit(env, hockeyist, unit):
    distance = geometry.distance(hockeyist, unit)
    angle = geometry.unit_angle_to(hockeyist, unit)

    return distance <= env.game.stick_length and abs(angle) <= env.game.stick_sector / 2.


def can_strike_unit(env, unit):
    return hockeyist_can_strike_unit(env, env.me, unit)


def hockeyist_with_puck(env):
    for h in env.world.hockeyists:
        if h.id == env.world.puck.owner_hockeyist_id:
            return h
    return None


def strike_power(env, swing_ticks):
    return env.game.strike_power_base_factor + env.game.strike_power_growth_factor * swing_ticks


def puck_speed_abs_after_strike(env, hockeyist):
    return (
        20. * strike_power(env, hockeyist.swing_ticks) +
        hockeyist.speed_x * math.cos(hockeyist.angle) +
        hockeyist.speed_y * math.sin(hockeyist.angle)
    )


def take_puck_probability(env, puck_speed):
    return max(0, 1.6 - 0.05 * puck_speed)


def team_size(env):
    return len(my_field_hockeyists(env))


def my_hockeyist_by_index(env, index):
    for h in env.world.hockeyists:
        if h.teammate and h.teammate_index == index:
            return h
    return None
