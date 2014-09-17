# -*- coding: utf-8 -*-

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
import prediction


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.strike_points = experiments.count_strike_points(env)
            self.weak_points = experiments.count_weak_points(env)
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

    def opponent_protect_goal(self, env, goal_point):
        opponent_player = shortcuts.opponent_player(env)
        point = geometry.Point(
            opponent_player.net_front,
            0.5 * (opponent_player.net_bottom + opponent_player.net_top)
        )
        radius = env.game.goal_net_height / 2.

        for h in shortcuts.opponent_field_hockeyists(env):
            if h.get_distance_to_unit(point) <= radius:
                return True
        return False

    def attack_with_puck(self, env):
        # FIXME кататься и вверх, и вниз
        middle_x = (env.game.rink_right + env.game.rink_left) / 2.
        corner_point = geometry.Point(
            middle_x,
            env.game.rink_top + 30
        )
        goal_point = experiments.get_goal_point(env)

        # FIXME учитывать, с какой стороны оппонент, подогнать коэффициент
        if env.me.x > middle_x and env.me.get_distance_to_unit(corner_point) > 30:
            env.move.turn = env.me.get_angle_to_unit(corner_point)
            env.move.speed_up = 1.0
            return

        if geometry.interval_point_distance(corner_point, goal_point, env.me) > 30:
            collega = filter(
                lambda h: h.id != env.me.id,
                shortcuts.my_field_hockeyists(env)
            )[0]
            angle = env.me.get_angle_to_unit(collega)
            env.move.turn = angle
            if abs(angle) <= env.game.pass_sector / 2.:
                env.move.action = ActionType.PASS
                env.move.pass_angle = angle
            return

        # strike_point = shortcuts.nearest_unit(self.strike_points, env.me)

        # if env.me.get_distance_to_unit(strike_point) >= 60:
        #     experiments.fast_move_to_point(env, strike_point)
        #     return

        basic_actions.turn_to_unit(env, goal_point)

        if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
            if self.opponent_protect_goal(env, goal_point):
                env.move.action = ActionType.SWING
            else:
                env.move.action = ActionType.STRIKE

    def attack_without_puck(self, env):
        nearest_opponent = shortcuts.nearest_unit(
            shortcuts.opponent_field_hockeyists(env), env.me)

        distance = env.me.get_distance_to_unit(nearest_opponent)
        angle = env.me.get_angle_to_unit(nearest_opponent)
        if distance > env.game.stick_length:
            env.move.speed_up = 1.0
        env.move.turn = angle

        if shortcuts.can_strike_unit(env, nearest_opponent):
            env.move.action = ActionType.STRIKE

    def its_dangerous(self, env):
        for wp in self.weak_points:
            if env.world.puck.get_distance_to_unit(wp) <= 90:
                return True
        return False

    def do_defence_actions(self, env):
        my_player_nearest_to_puck = shortcuts.nearest_unit(
            shortcuts.my_field_hockeyists(env),
            env.world.puck)
        if my_player_nearest_to_puck.id == env.me.id:
            self.do_active_defence_action(env)
        else:
            self.do_protect_goal_actions(env)

    def do_active_defence_action(self, env):
        env.move.speed_up = 1.0
        env.move.turn = env.me.get_angle_to_unit(env.world.puck)

        if self.its_dangerous(env):
            hockeyist_with_puck = shortcuts.hockeyist_with_puck(env)
            if hockeyist_with_puck is not None:
                if shortcuts.can_strike_unit(env, hockeyist_with_puck):
                    env.move.action = ActionType.STRIKE
                    return

        if shortcuts.can_take_puck(env):
            env.move.action = ActionType.TAKE_PUCK
        # for oh in shortcuts.opponent_field_hockeyists(env):
            # if shortcuts.can_strike_unit(env, oh):
            #     env.move.action = ActionType.STRIKE

    def do_protect_goal_actions(self, env):
        env.move.action = ActionType.TAKE_PUCK
        if env.me.get_distance_to_unit(self.defence_point) >= 30:
            experiments.fast_move_to_point(env, self.defence_point)
        else:
            basic_actions.turn_to_unit(env, env.world.puck)
