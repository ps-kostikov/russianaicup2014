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

    end = False
    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return
        if self.end:
            return

        env = environment.Environment(me, world, game, move)

        def count_strike_point(env):
            opponent_player = shortcuts.opponent_player(env)
            # uu = Unit(0,0,0,opponent_player.net_front, env.game.goal_net_top + env.game.goal_net_height, 0,0,0,0)
            # geometry.rad_to_degree(uu.get_angle_to(env.game.rink_left / 2. + env.game.rink_right /2. , env.game.rink_top))

            # import ipdb; ipdb.set_trace()
            return geometry.ray_interval_intersection_v2(
                geometry.Point(opponent_player.net_front, env.game.goal_net_top + env.game.goal_net_height),
                geometry.Point(math.cos(geometry.degree_to_rad(-150)), math.sin(geometry.degree_to_rad(-150))),
                geometry.Point(0, env.game.goal_net_top - 100),
                geometry.Point(world.width, env.game.goal_net_top - 100),
            )

            # return geometry.Point(game.rink_right - 300, game.goal_net_top - game.puck_binding_range)

        if world.tick == 0:
            actions = [
                training_actions.WaitForTick(100),
                training_actions.TakePuck(),
                training_actions.Stop(),
                training_actions.MoveToPoint(
                    count_strike_point(env)
                ),
                training_actions.Stop(),
                training_actions.TurnToGoal(),
                training_actions.Strike(20),
            ]
            self.action_list = training_actions.ActionList(*actions)


        # if world.tick == 0:
        #     self.action_list = training_actions.ActionList(
        #         training_actions.WaitForTick(100),
        #         training_actions.TakePuck(),
        #         training_actions.Stop(),
        #         training_actions.MoveToPoint(
        #             geometry.Point(shortcuts.field_center(env).y, shortcuts.opponent_player(env).net_top)
        #         ),
        #         training_actions.Stop(),
        #         training_actions.MoveToPoint(
        #             geometry.Point(world.width - 350, shortcuts.opponent_player(env).net_top)
        #         ),

        #         # training_actions.MoveToPoint(
        #         #     geometry.Point(380, shortcuts.field_center(env).y)
        #         # ),
        #         training_actions.Stop(),
        #     )


        if self.action_list.do(env):
            return

        # x1 = world.puck.x
        # y1 = world.puck.y
        # vx2 = world.puck.speed_x
        # vy2 = world.puck.speed_y
        # x3 = game.rink_right
        # y3 = game.goal_net_top + game.goal_net_height
        # x4 = game.rink_right + game.goal_net_width
        # y4 = game.goal_net_top + game.goal_net_height

        # print 'vx2, vy2', vx2, vy2
        # if geometry.ray_interval_intersection(x1, y1, vx2, vy2, x3, y3, x4, y4):
        if prediction.goalie_can_save_straight(env):
            print 'FUCK YOU'
        else:
            print 'GOAL'

        self.end = True

        # import ipdb; ipdb.set_trace()
        # goal = get_goal_point(env)
        # angle = me.get_angle_to_unit(goal)
        # move.pass_angle = angle
        # move.pass_power = 1.
        # env.move.action = ActionType.PASS

