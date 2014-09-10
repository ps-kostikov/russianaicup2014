import math
from model.ActionType import ActionType
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

import geometry


class MyStrategy:

    target_x, target_y = 0, 0

    def move(self, me, world, game, move):
        angle = me.get_angle_to(self.target_x, self.target_y)
        move.turn = angle
        if abs(angle) < geometry.degree_to_rad(1):
            move.speed_up = 1.

