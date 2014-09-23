# -*- coding: utf-8 -*-

import prediction
import geometry
import shortcuts

import math


def _count_player_weak_points(env, player):
    is_left = 1. if player.net_back < shortcuts.rink_center(env).x else -1.
    return [
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top - 50
        ),
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top + env.game.goal_net_height + 50
        )
    ]


def count_strike_points(env):
    return _count_player_weak_points(
        env,
        shortcuts.opponent_player(env)
    )


def count_weak_points(env):
    return _count_player_weak_points(
        env,
        shortcuts.my_player(env)
    )


def count_attack_polygon(
    env, player, is_down, angle_min, angle_max, rink_margin, middle_margin):

    is_left = shortcuts.player_left(env, player)
    left_sign = shortcuts.player_left_sign(env, player)
    left_sign = 1 if is_left else -1

    # down_sign = 1 - нижняя половина
    down_sign = 1 if is_down else -1.

    if is_down:
        corner_y = player.net_top
    else:
        corner_y = player.net_bottom

    corner = geometry.Point(
        player.net_front,
        corner_y)

    # attack_y_min - линия ближе к границе
    # attack_y_max - линия ближе к воротам
    if is_down:
        attack_y_min = env.game.rink_bottom - rink_margin
    else:
        attack_y_min = env.game.rink_top + rink_margin
    if is_down:
        attack_y_max = player.net_bottom - shortcuts.goalie_radius() - middle_margin
    else:
        attack_y_max = player.net_top + shortcuts.goalie_radius() + middle_margin

    attack_x_min = env.game.rink_left
    attack_x_max = env.game.rink_right

    angle_sign = left_sign * down_sign
    if is_left:
        angle_shift = 0.
    else:
        angle_shift = geometry.degree_to_rad(180)

    p1 = geometry.ray_interval_intersection_v2(
        corner,
        geometry.angle_vector(angle_sign * angle_min + angle_shift, 1),
        geometry.Point(attack_x_min, attack_y_max),
        geometry.Point(attack_x_max, attack_y_max)
    )
    p2 = geometry.ray_interval_intersection_v2(
        corner,
        geometry.angle_vector(angle_sign * angle_min + angle_shift, 1),
        geometry.Point(attack_x_min, attack_y_min),
        geometry.Point(attack_x_max, attack_y_min)
    )
    p3 = geometry.ray_interval_intersection_v2(
        corner,
        geometry.angle_vector(angle_sign * angle_max + angle_shift, 1),
        geometry.Point(attack_x_min, attack_y_min),
        geometry.Point(attack_x_max, attack_y_min)
    )
    p4 = geometry.ray_interval_intersection_v2(
        corner,
        geometry.angle_vector(angle_sign * angle_max + angle_shift, 1),
        geometry.Point(attack_x_min, attack_y_max),
        geometry.Point(attack_x_max, attack_y_max)
    )
    return geometry.Polygon([p1, p2, p3, p4])


def count_optimistic_attack_polygons(env, player):
    return [
        count_attack_polygon(env, player, is_down,
            geometry.degree_to_rad(30), geometry.degree_to_rad(50), 0, 0)
        for is_down in (False, True)
    ]


def count_cautious_attack_polygons(env, player):
    return [
        count_attack_polygon(env, player, is_down,
            geometry.degree_to_rad(27), geometry.degree_to_rad(55), 0, -100)
        for is_down in (False, True)
    ]


def count_target_up_attack_polygon(env, player):
    return count_attack_polygon(
        env, player, False,
        geometry.degree_to_rad(35), geometry.degree_to_rad(50), 50, 150
    )


def count_target_down_attack_polygon(env, player):
    return count_attack_polygon(
        env, player, True,
        geometry.degree_to_rad(35), geometry.degree_to_rad(50), 50, 150
    )


def count_attack_polygons(env, player):
    is_left = shortcuts.player_left(env, player)
    left_sign = shortcuts.player_left_sign(env, player)
    left_sign = 1 if is_left else -1

    angle_min = geometry.degree_to_rad(37)
    angle_max = geometry.degree_to_rad(53)

    polygons = []
    # down_sign = 1 - нижняя половина
    for down_sign in (-1, 1):
        is_down = down_sign > 0

        if is_down:
            corner_y = player.net_top
        else:
            corner_y = player.net_bottom

        corner = geometry.Point(
            player.net_front,
            corner_y)

        # attack_y_min - линия ближе к границе
        # attack_y_max - линия ближе к воротам
        if is_down:
            attack_y_min = env.game.rink_bottom - 30
        else:
            attack_y_min = env.game.rink_top + 30
        if is_down:
            attack_y_max = player.net_bottom - shortcuts.goalie_radius() - 30
        else:
            attack_y_max = player.net_top + shortcuts.goalie_radius() + 30

        attack_x_min = env.game.rink_left
        attack_x_max = env.game.rink_right

        angle_sign = left_sign * down_sign
        if is_left:
            angle_shift = 0.
        else:
            angle_shift = geometry.degree_to_rad(180)

        p1 = geometry.ray_interval_intersection_v2(
            corner,
            geometry.angle_vector(angle_sign * angle_min + angle_shift, 1),
            geometry.Point(attack_x_min, attack_y_max),
            geometry.Point(attack_x_max, attack_y_max)
        )
        p2 = geometry.ray_interval_intersection_v2(
            corner,
            geometry.angle_vector(angle_sign * angle_min + angle_shift, 1),
            geometry.Point(attack_x_min, attack_y_min),
            geometry.Point(attack_x_max, attack_y_min)
        )
        p3 = geometry.ray_interval_intersection_v2(
            corner,
            geometry.angle_vector(angle_sign * angle_max + angle_shift, 1),
            geometry.Point(attack_x_min, attack_y_min),
            geometry.Point(attack_x_max, attack_y_min)
        )
        p4 = geometry.ray_interval_intersection_v2(
            corner,
            geometry.angle_vector(angle_sign * angle_max + angle_shift, 1),
            geometry.Point(attack_x_min, attack_y_max),
            geometry.Point(attack_x_max, attack_y_max)
        )
        polygons.append(geometry.Polygon([p1, p2, p3, p4]))

    return polygons


def count_defence_point(env):
    im_left_sign = shortcuts.im_left_sign(env)
    my_player = shortcuts.my_player(env)
    return geometry.Point(
        my_player.net_front + im_left_sign * 90,
        shortcuts.field_center(env).y
    )


def fast_move_to_point(env, point):
    distance = env.me.get_distance_to_unit(point)
    mirrow_point = geometry.Point(
        2 * env.me.x - point.x,
        2 * env.me.y - point.y
    )
    time_turn_forward = abs(env.me.get_angle_to_unit(point)) / env.game.hockeyist_turn_angle_factor
    time_move_forward = prediction.count_n_by_x(
        0, 0, env.game.hockeyist_speed_up_factor, distance)

    time_turn_backward = abs(env.me.get_angle_to_unit(mirrow_point)) / env.game.hockeyist_turn_angle_factor
    time_move_backward = prediction.count_n_by_x(
        0, 0, env.game.hockeyist_speed_down_factor, distance)
    if time_turn_backward + time_move_backward > time_turn_forward + time_move_forward:
        fast_move_to_point_forward(env, point)
    else:
        fast_move_to_point_backward(env, point)


def fast_move_to_point_forward(env, point):
    distance = env.me.get_distance_to_unit(point)
    angle = env.me.get_angle_to_unit(point)

    if abs(angle) > geometry.degree_to_rad(1):
        env.move.turn = angle
        return

    v0 = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
    vn = 0
    a = -env.game.hockeyist_speed_down_factor
    n = prediction.count_n(v0, a, vn)

    if n is None:
        env.move.speed_up = 1.0
        return

    n = round(n) + 1
    x0 = 0.
    xn = prediction.count_xn(x0, v0, a, n)

    if xn > distance:
        env.move.speed_up = -1.0
    else:
        env.move.speed_up = 1.0


def fast_move_to_point_backward(env, point):
    distance = env.me.get_distance_to_unit(point)
    mirrow_point = geometry.Point(
        2 * env.me.x - point.x,
        2 * env.me.y - point.y
    )
    angle = env.me.get_angle_to_unit(mirrow_point)

    if abs(angle) > geometry.degree_to_rad(1):
        env.move.turn = angle
        return

    v0 = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
    vn = 0
    a = -env.game.hockeyist_speed_up_factor
    n = prediction.count_n(v0, a, vn)

    if n is None:
        env.move.speed_up = -1.0
        return

    n = round(n) + 1
    x0 = 0.
    xn = prediction.count_xn(x0, v0, a, n)

    if xn > distance:
        env.move.speed_up = 1.0
    else:
        env.move.speed_up = -1.0


def do_stop(env):
    speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
    angle = geometry.get_angle(
        math.cos(env.me.angle), math.sin(env.me.angle),
        env.me.speed_x, env.me.speed_y)
    if abs(geometry.rad_to_degree(angle)) < 90:
        env.move.turn = angle
        env.move.speed_up = -min(1., speed_abs / env.game.hockeyist_speed_down_factor)
    else:
        env.move.turn = -angle
        env.move.speed_up = min(1., speed_abs / env.game.hockeyist_speed_up_factor)


def get_goal_point(env, puck=None):
    opponent_player = env.world.get_opponent_player()
    goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
    goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
    if puck is None:
        puck = env.world.puck
    goal_y += (0.5 if puck.y < goal_y else -0.5) * env.game.goal_net_height
    return geometry.Point(goal_x, goal_y)

