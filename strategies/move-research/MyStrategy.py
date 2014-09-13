import math
from model.ActionType import ActionType
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

import environment


def predict_speed(env):
    a = env.game.hockeyist_speed_up_factor
    k = 0.98
    n = env.world.tick + 1
    return (a * k) * (1 - k ** n) / (1 - k)
    # return (env.me.speed_x - env.game.hockeyist_speed_down_factor) * 0.98
    # return (env.me.speed_x + env.game.hockeyist_speed_up_factor) * 0.98


def predict_pos(env):
    a = env.game.hockeyist_speed_up_factor
    x0 = 362
    n = env.world.tick + 1
    k = 0.98
    q = k / (1. - k)
    return x0 + n * a * q - a * (q ** 2) * (1. - k ** n)
    # return env.me.x + predict_speed(env)


class MyStrategy:

    target_x, target_y = 0, 0

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.expected_speed_x = 0.
            self.expected_x = me.x
            self.a = 1

        print self.a

        move.speed_up = 1.0
        print (
            'tick =', world.tick,
            'speed_x =', me.speed_x,
            # 'expected_speed_x =', self.expected_speed_x,
            # 'diff speed = ', abs(me.speed_x - self.expected_speed_x),
            "x = ", me.x,
            'expected_x = ', self.expected_x,
            'diff x = ', abs(me.x - self.expected_x)
        )

        self.expected_speed_x = predict_speed(env)
        self.expected_x = predict_pos(env)

        if world.tick > 10:
            import ipdb; ipdb.set_trace()

