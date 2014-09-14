from model.ActionType import ActionType
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

import geometry
import experiments
import environment
import shortcuts
import basic_actions


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.strike_points = experiments.count_strike_points(env)
            self.defence_point = experiments.count_defence_point(env)

        if env.me.state == HockeyistState.SWINGING:
            if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
                env.move.action = ActionType.STRIKE
            else:
                env.move.action = ActionType.SWING
            return

        if self.attack_mode(env):
            self.do_attack_actions(env)
        else:
            self.do_defence_actions(env)

    def attack_mode(self, env):
        if env.world.puck.owner_player_id is not None:
            return env.world.puck.owner_player_id == env.me.player_id
        nearest_hockeyist = shortcuts.nearest_unit(
            shortcuts.field_hockeyists(env),
            env.world.puck
        )
        return nearest_hockeyist.player_id == env.me.player_id

    def do_attack_actions(self, env):

        if env.world.puck.owner_hockeyist_id == env.me.id:
            self.attack_with_puck(env)
        else:
            self.do_protect_goal_actions(env)
            # self.attack_without_puck(env)

    def attack_with_puck(self, env):
        strike_point = shortcuts.nearest_unit(self.strike_points, env.me)

        if env.me.get_distance_to_unit(strike_point) >= 60:
            experiments.fast_move_to_point(env, strike_point)
            return

        goal_point = experiments.get_goal_point(env)
        basic_actions.turn_to_unit(env, goal_point)

        if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
            env.move.action = ActionType.SWING

    def attack_without_puck(self, env):
        nearest_opponent = shortcuts.nearest_unit(
            shortcuts.opponent_field_hockeyists(env), env.me)
        if env.me.get_distance_to_unit(nearest_opponent) > env.game.stick_length:
            env.move.speed_up = 1.0
        elif abs(env.me.get_angle_to_unit(nearest_opponent)) < 0.5 * env.game.stick_sector:
            env.move.action = ActionType.STRIKE
        env.move.turn = env.me.get_angle_to_unit(nearest_opponent)

    def do_defence_actions(self, env):
        nearest_to_puck = shortcuts.nearest_unit(
            shortcuts.my_field_hockeyists(env), env.world.puck)
        if nearest_to_puck.id == env.me.id:
            self.do_get_puck_actions(env)
        else:
            self.do_protect_goal_actions(env)

    def do_get_puck_actions(self, env):
        env.move.speed_up = 1.0
        env.move.turn = env.me.get_angle_to_unit(env.world.puck)
        env.move.action = ActionType.TAKE_PUCK

    def do_protect_goal_actions(self, env):
        env.move.action = ActionType.TAKE_PUCK
        if env.me.get_distance_to_unit(self.defence_point) >= 30:
            experiments.fast_move_to_point(env, self.defence_point)
        else:
            basic_actions.turn_to_unit(env, env.world.puck)

