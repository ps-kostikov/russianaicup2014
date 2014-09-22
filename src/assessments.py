import prediction
import geometry
import shortcuts

import math


def puck_is_heading_to_my_net(env):
    player = shortcuts.my_player(env)
    pbegin = geometry.Point(
        player.net_front,
        env.game.rink_top
    )
    pend = geometry.Point(
        player.net_front,
        env.game.rink_bottom
    )
    intersection = geometry.ray_interval_intersection_v2(
        env.world.puck,
        geometry.Point(
            env.world.puck.speed_x,
            env.world.puck.speed_y
        ),
        pbegin,
        pend
    )
    if intersection is None:
        return False
    return abs(intersection.y - player.net_top) < 50 or abs(intersection.y - player.net_bottom) < 50


def ticks_to_reach_point(env, hockeyist, point):
    distance = geometry.distance(hockeyist, point)
    if distance < 0.01:
        return 0
    angle = hockeyist.get_angle_to_unit(point)
    v0 = (
        hockeyist.speed_x * (point.x - hockeyist.x) +
        hockeyist.speed_y * (point.y - hockeyist.y)
    ) / distance

    a = env.game.hockeyist_speed_up_factor
    ticks_for_move = prediction.count_n_by_x(0, v0, a, distance)
    return abs(angle) / env.game.hockeyist_turn_angle_factor + ticks_for_move


def someone_can_reach_me_after_ticks(env, ticks):
    opponent_hockeyists = shortcuts.opponent_field_hockeyists(env)
    for h in opponent_hockeyists:
        for t in range(ticks + 1):
            future_h = prediction.next_hockeyist_position(env, h, t)
            if shortcuts.hockeyist_can_strike_unit(env, future_h, env.me):
                return True
            if shortcuts.hockeyist_can_take_puck(env, future_h):
                return True
    return False

# 1dim model
def _count_ricochet(minx, maxx, x):
    while x > maxx or x < minx:
        if x > maxx:
            x = 2 * maxx - x
        if x < minx:
            x = 2 * minx - x
    return x


def unit_position_after(env, unit, ticks):
    virtual_point = geometry.Point(
        unit.x + unit.speed_x * ticks,
        unit.y + unit.speed_y * ticks
    )
    return geometry.Point(
        _count_ricochet(env.game.rink_left, env.game.rink_right, virtual_point.x),
        _count_ricochet(env.game.rink_top, env.game.rink_bottom, virtual_point.y)
    )


def can_goal(env, hockeyist, player):
    if env.world.puck.owner_hockeyist_id != hockeyist.id:
        return False

    speed_abs = shortcuts.puck_speed_abs_after_strike(env, hockeyist)

    puck_after_strike = prediction.UnitShadow(
        env.world.puck.x,
        env.world.puck.y,
        speed_abs * math.cos(hockeyist.angle),
        speed_abs * math.sin(hockeyist.angle)
    )

    return not prediction.goalie_can_save_straight(env, puck=puck_after_strike)


def puck_after_strike(env, hockeyist=None, puck=None):
    if hockeyist is None:
        hockeyist = env.me
    if puck is None:
        puck = env.world.puck

    speed_abs = shortcuts.puck_speed_abs_after_strike(env, hockeyist)

    speed = geometry.adjust_vector(geometry.Point(
        puck.x - hockeyist.x,
        puck.y - hockeyist.y
    ), speed_abs)

    return prediction.UnitShadow(
        puck.x,
        puck.y,
        speed.x,
        speed.y,
        angle=env.world.puck.angle
    )
