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


class MyStrategy:

    def move(self, me, world, game, move):
        if me.teammate_index != 0:
            return

        env = environment.Environment(me, world, game, move)

        def get_goal_point(env):
            opponent_player = env.world.get_opponent_player()
            goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
            goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
            goal_y += 0.5 * env.game.goal_net_height
            return geometry.Point(goal_x, goal_y)

        # if world.tick == 0:
        #     self.action_list = training_actions.ActionList(
        #         training_actions.WaitForTick(100),
        #         training_actions.TakePuck(),
        #         training_actions.Stop(),
        #         training_actions.MoveToPoint(
        #             geometry.Point(400, game.goal_net_top)
        #         ),
        #         training_actions.Stop(),
        #         training_actions.TurnToPoint(get_goal_point(env)),
        #         training_actions.Strike(20)
        #     )

        if world.tick == 0:
            self.action_list = training_actions.ActionList(
                training_actions.WaitForTick(100),
                training_actions.TakePuck(),
                training_actions.Stop(),
                training_actions.MoveToPoint(
                    geometry.Point(shortcuts.field_center(env).y, shortcuts.opponent_player(env).net_top)
                ),
                training_actions.Stop(),
                training_actions.MoveToPoint(
                    geometry.Point(350, shortcuts.opponent_player(env).net_top)
                ),

                # training_actions.MoveToPoint(
                #     geometry.Point(380, shortcuts.field_center(env).y)
                # ),
                training_actions.Stop(),
            )


        if self.action_list.do(env):
            return

        goal = get_goal_point(env)
        angle = me.get_angle_to_unit(goal)
        move.pass_angle = angle
        move.pass_power = 1.
        env.move.action = ActionType.PASS

