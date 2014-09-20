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

import shortcuts
import environment
import geometry
import measurements
import prediction


class MyStrategy:

    def move(self, me, world, game, move):
        env = environment.Environment(me, world, game, move)
        import ipdb; ipdb.set_trace()
