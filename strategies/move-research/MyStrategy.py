import math
from model.ActionType import ActionType
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World


def predict_speed(me):
    # return me.speed_x * 0.98 + 0.113425938288
    return me.speed_x * 0.98 - 0.0680555582047


class MyStrategy:

    target_x, target_y = 0, 0

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        if world.tick == 0:
            self.expected_speed_x = 0.
            self.a = 1

        print self.a

        move.speed_up = -1.0
        print world.tick, 'speed_x =', me.speed_x, 'expected_speed_x =', self.expected_speed_x, 'diff = ', abs(me.speed_x - self.expected_speed_x)

        self.expected_speed_x = predict_speed(me)

        if world.tick > 100:
            import ipdb; ipdb.set_trace()

