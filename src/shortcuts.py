from model.HockeyistType import HockeyistType

import geometry


def my_player(env):
    return env.world.get_my_player()


def opponent_player(env):
    return env.world.get_opponent_player()


def opponent_goal_interval(env):
    op = opponent_player(env)
    return [
        geometry.Point(op.net_front, op.net_top),
        geometry.Point(op.net_front, op.net_bottom),
    ]


def goalie(env, player):
    for h in env.world.hockeyists:
        if h.player_id == player.id and h.type == HockeyistType.GOALIE:
            return h
    return None


def my_goalie(env):
    return goalie(env, my_player(env))


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


def im_left(env):
    return 1. if my_player(env).net_back < rink_center(env).x else -1.


def my_field_hockeyists(env):
    return filter(
        lambda h: h.teammate and h.type != HockeyistType.GOALIE,
        env.world.hockeyists)


def opponent_field_hockeyists(env):
    return filter(
        lambda h: not h.teammate and h.type != HockeyistType.GOALIE,
        env.world.hockeyists)


def field_hockeyists(env):
    return filter(
        lambda h: h.type != HockeyistType.GOALIE,
        env.world.hockeyists)


def nearest_unit(units, target):
    return min(
        *units,
        key=lambda u: geometry.distance(u, target)
    )


def can_take_puck(env):
    distance = env.me.get_distance_to_unit(env.world.puck)
    angle = env.me.get_angle_to_unit(env.world.puck)

    return distance <= env.game.stick_length and abs(angle) <= env.game.stick_sector / 2.


def can_strike_unit(env, unit):
    distance = env.me.get_distance_to_unit(unit)
    angle = env.me.get_angle_to_unit(unit)

    return distance <= env.game.stick_length and abs(angle) <= env.game.stick_sector / 2.


def hockeyist_with_puck(env):
    for h in env.world.hockeyists:
        if h.id == env.world.puck.owner_hockeyist_id:
            return h
    return None
