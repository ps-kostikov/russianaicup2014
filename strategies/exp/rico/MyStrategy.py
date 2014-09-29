import math

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

import training_actions
import environment
import shortcuts
import geometry
import prediction


class MyStrategy:

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            actions = [
                training_actions.TakePuck(),
                training_actions.Stop(),
                # training_actions.TurnToPoint(
                #     geometry.Point(env.game.rink_right, env.game.rink_top + 100)
                # ),
                training_actions.TurnToPoint(
                    shortcuts.my_goalie(env)
                ),
                training_actions.Strike(20),
            ]
            self.action_list = training_actions.ActionList(*actions)

        if self.action_list.do(env):
            return

        puck_speed_abs = geometry.vector_abs(env.world.puck.speed_x, env.world.puck.speed_y)
        print env.world.tick, 'x = ', env.world.puck.speed_x, 'y = ', env.world.puck.speed_y

