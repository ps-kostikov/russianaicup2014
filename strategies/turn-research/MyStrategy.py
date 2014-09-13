from model.ActionType import ActionType
from model.Game import Game
from model.Hockeyist import Hockeyist
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Move import Move
from model.Player import Player
from model.PlayerContext import PlayerContext
from model.Puck import Puck
from model.Unit import Unit
from model.World import World

import geometry
import environment


def predict_andle(env):
    return env.me.angle + env.game.hockeyist_turn_angle_factor


class MyStrategy:

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.expected_angle = me.angle

        move.turn = geometry.degree_to_rad(10)
        print (
            'tick = ', world.tick,
            'angle = ', geometry.rad_to_degree(me.angle),
            'expected_angle =', geometry.rad_to_degree(self.expected_angle),
            'diff = ', geometry.rad_to_degree(abs(self.expected_angle - me.angle)),
            'angular_speed = ', geometry.rad_to_degree(me.angular_speed)
        )

        self.expected_angle = predict_andle(env)


        if world.tick >= 20:
            import ipdb; ipdb.set_trace()
