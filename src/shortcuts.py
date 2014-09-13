from model.HockeyistType import HockeyistType

import geometry


def my_player(env):
    return env.world.get_my_player()


def opponent_player(env):
    return env.world.get_opponent_player()


def my_goalie(env):
    my_player = env.world.get_my_player()
    for h in env.world.hockeyists:
        if h.player_id == my_player.id and h.type == HockeyistType.GOALIE:
            return h
    return None


def field_center(env):
    my_player = env.world.get_my_player()
    opponent_player = env.world.get_opponent_player()

    x = (my_player.net_left + opponent_player.net_right) / 2.
    y = (my_player.net_top + my_player.net_bottom) / 2.

    return geometry.Point(x, y)
