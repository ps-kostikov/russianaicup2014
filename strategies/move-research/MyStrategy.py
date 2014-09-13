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
    return (env.me.speed_x - env.game.hockeyist_speed_down_factor) * 0.98
    # return (env.me.speed_x + env.game.hockeyist_speed_up_factor) * 0.98
    # return env.me.speed_x * 0.98 + 0.113425938288
    # return env.me.speed_x * 0.98 - 0.0680555582047


class MyStrategy:

    target_x, target_y = 0, 0

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.expected_speed_x = 0.
            self.a = 1

        print self.a

        move.speed_up = -1.0
        print world.tick, 'speed_x =', me.speed_x, 'expected_speed_x =', self.expected_speed_x, 'diff = ', abs(me.speed_x - self.expected_speed_x)

        self.expected_speed_x = predict_speed(env)

        if world.tick > 100:
            import ipdb; ipdb.set_trace()

