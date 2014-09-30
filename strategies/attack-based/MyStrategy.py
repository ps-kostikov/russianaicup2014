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
import assessments
import algorithm


def _count_player_weak_points(env, player):
    is_left = 1. if player.net_back < shortcuts.rink_center(env).x else -1.
    return [
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top - 50
        ),
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top + env.game.goal_net_height + 50
        )
    ]


def count_weak_points(env):
    return _count_player_weak_points(
        env,
        shortcuts.my_player(env)
    )


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.attack_polygons = experiments.count_attack_polygons(
                env,
                shortcuts.opponent_player(env))
            self.weak_points = count_weak_points(env)

        if env.me.state == HockeyistState.SWINGING:
            if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
                env.move.action = ActionType.STRIKE
            elif assessments.someone_can_reach_me_after_ticks(env, 2):
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
            self.attack_without_puck(env)

    def opponent_protect_goal(self, env, goal_point):

        for h in shortcuts.opponent_field_hockeyists(env):
            distance = geometry.ray_point_distance(
                env.world.puck,
                geometry.diff(env.world.puck, goal_point),
                h
            )
            if distance <= h.radius:
                return True
        return False

    def attack_with_puck(self, env):
        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.attack_polygons):
            strike_point = env.me

        else:
            strike_point = algorithm.best_point_for_polynoms(
                self.attack_polygons,
                f=lambda p: -assessments.ticks_to_reach_point(env, env.me, p))
        # strike_point = geometry.convex_polygons_nearest_point(
        #     self.attack_polygons, env.me)

        if env.me.get_distance_to_unit(strike_point) >= 60:
            # print strike_point
            experiments.fast_move_to_point(env, strike_point)
            return

        goal_point = experiments.get_goal_point(env)
        basic_actions.turn_to_unit(env, goal_point)

        if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
            # if self.opponent_protect_goal(env, goal_point):
            #     env.move.action = ActionType.SWING
            # else:
            #     env.move.action = ActionType.STRIKE
            env.move.action = ActionType.SWING

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

