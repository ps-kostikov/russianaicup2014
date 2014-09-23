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
import assessments
import algorithm
import prediction


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            op = shortcuts.opponent_player(env)
            mp = shortcuts.my_player(env)
            self.attack_polygons = experiments.count_optimistic_attack_polygons(
                env, op)
            self.target_polygons = [
                experiments.count_target_up_attack_polygon(env, op),
                experiments.count_target_down_attack_polygon(env, op),
            ]
            self.defence_point = experiments.count_defence_point(env)
            self.weak_polygons = experiments.count_cautious_attack_polygons(
                env, mp)
            self.dead_polygons = experiments.count_dead_polygons(env, op)

            self.last_puck_owner_player_id = None

        self.save_last_puck_owner(env)

        if env.me.state == HockeyistState.SWINGING:
            if self.swing_condition(env):
                env.move.action = ActionType.SWING

            if self.strike_condition(env):
                env.move.action = ActionType.STRIKE

            return

        hockeyist_with_puck = shortcuts.hockeyist_with_puck(env)
        my_nearest_hockeyist = min(
            shortcuts.my_field_hockeyists(env),
            key=lambda h: assessments.ticks_to_reach_point(env, h, env.world.puck)
        )
        if hockeyist_with_puck is None or hockeyist_with_puck.player_id != env.me.player_id:
            if my_nearest_hockeyist.id == me.id:
                self.do_get_puck_actions(env)
            else:
                self.do_protect_goal_actions(env)
        elif hockeyist_with_puck.player_id == env.me.player_id:
            if hockeyist_with_puck.id == env.me.id:
                self.attack_with_puck(env)
            else:
                self.do_protect_goal_actions(env)

    def save_last_puck_owner(self, env):
        hockeyist_with_puck = shortcuts.hockeyist_with_puck(env)
        if hockeyist_with_puck is not None:
            self.last_puck_owner_player_id = hockeyist_with_puck.player_id

    def strike_condition(self, env):
        if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
            return True
        if assessments.someone_can_reach_me_after_ticks_rough(env, 2):
            next_puck = assessments.puck_after_strike(env, hockeyist=env.me)
            goal_point = experiments.get_goal_point(env)
            if basic_actions.turned_to_unit(env, goal_point):
                return True

        if env.me.state == HockeyistState.SWINGING:
            next_puck = prediction.next_puck_position(env)
            next_me = prediction.next_hockeyist_position(env, env.me, 1)
            # HARDCODE
            next_me.swing_ticks = min(20, env.me.swing_ticks + 1)
            after_strike = assessments.puck_after_strike(env, hockeyist=next_me, puck=next_puck)
            if prediction.goalie_can_save_straight(env, puck=after_strike):
                return True

        return False

    def swing_condition(self, env):
        puck = assessments.puck_after_strike(env)
        return not prediction.goalie_can_save_straight(env, puck=puck)

    def pass_condition(self, env, strike_point):
        collega = filter(
            lambda h: h.id != env.me.id,
            shortcuts.my_field_hockeyists(env)
        )[0]
        if geometry.distance(collega, env.me) > 200:
            for oh in shortcuts.opponent_field_hockeyists(env):
                if geometry.interval_point_distance(env.me, strike_point, oh) < 60:
                    return True

        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.dead_polygons):
            return True
        return False

    def attack_with_puck(self, env):
        def f(point):
            nfc = shortcuts.net_front_center(env, shortcuts.opponent_player(env))
            angles = [
                min(
                    geometry.degree_to_rad(110),
                    geometry.ray_ray_angle(oh, env.me, point)
                )
                for oh in shortcuts.opponent_field_hockeyists(env)
                if geometry.distance(oh, nfc) > 300
            ]
            ticks_to_reach_point = assessments.ticks_to_reach_point(env, env.me, point)
            if not angles:
                return -ticks_to_reach_point
            return geometry.rad_to_degree(min(angles)) - ticks_to_reach_point / 100

        strike_point = algorithm.best_point_for_polynoms(
            self.target_polygons, f=f)

        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.attack_polygons):
            goal_point = experiments.get_goal_point(env)
            basic_actions.turn_to_unit(env, goal_point)

            if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
                env.move.speed_up = 1.

            if self.swing_condition(env):
                env.move.action = ActionType.SWING

            if self.strike_condition(env):
                env.move.action = ActionType.STRIKE
            return

        if self.pass_condition(env, strike_point):
            self.do_pass(env)
            return

        experiments.fast_move_to_point(env, strike_point)

    def its_dangerous(self, env):
        return (any(geometry.point_in_convex_polygon(env.world.puck, p) for p in self.weak_polygons)
            or geometry.distance(env.world.puck, self.defence_point) < 120)

    def do_get_puck_actions(self, env):
        if self.its_dangerous(env):
            hockeyist_with_puck = shortcuts.hockeyist_with_puck(env)
            if hockeyist_with_puck is not None:
                if shortcuts.can_strike_unit(env, hockeyist_with_puck):
                    env.move.action = ActionType.STRIKE
                    return

        env.move.speed_up = 1.0
        hwp = shortcuts.hockeyist_with_puck(env)
        if hwp is not None:
            basic_actions.turn_to_unit(env, hwp)
        else:
            basic_actions.turn_to_unit(env, env.world.puck)

        if shortcuts.can_take_puck(env):

            puck_abs_speed = geometry.vector_abs(env.world.puck.speed_x, env.world.puck.speed_y)
            if shortcuts.take_puck_probability(env, puck_abs_speed) >= 1.:
                env.move.action = ActionType.TAKE_PUCK
                return

            if not assessments.puck_is_heading_to_my_net(env):
                env.move.action = ActionType.TAKE_PUCK
                return

        if shortcuts.can_strike_unit(env, env.world.puck):
            env.move.action = ActionType.STRIKE
            return

    def do_pass(self, env):
        collega = filter(
            lambda h: h.id != env.me.id,
            shortcuts.my_field_hockeyists(env)
        )[0]
        angle = env.me.get_angle_to_unit(collega)
        env.move.turn = angle
        if abs(angle) <= env.game.pass_sector / 2.:
            env.move.action = ActionType.PASS
            env.move.pass_angle = angle
            env.move.pass_power = 0.8

    def leave_goal_condition(self, env):
        return geometry.distance(self.defence_point, env.world.puck) <= 200

    def do_protect_goal_actions(self, env):
        if shortcuts.can_take_puck(env):
            puck_abs_speed = geometry.vector_abs(env.world.puck.speed_x, env.world.puck.speed_y)
            if shortcuts.take_puck_probability(env, puck_abs_speed) >= 1.:
                env.move.action = ActionType.TAKE_PUCK
                return

            if not assessments.puck_is_heading_to_my_net(env):
                env.move.action = ActionType.TAKE_PUCK
                return

        if shortcuts.can_strike_unit(env, env.world.puck):
            env.move.action = ActionType.STRIKE
            return

        for oh in shortcuts.opponent_field_hockeyists(env):
            if shortcuts.can_strike_unit(env, oh):
                env.move.action = ActionType.STRIKE
                return

        if self.its_dangerous(env) and env.me.get_distance_to_unit(self.defence_point) < 100:
            basic_actions.turn_to_unit(env, env.world.puck)
            if self.leave_goal_condition(env):
                if basic_actions.turned_to_unit(env, env.world.puck):
                    env.move.speed_up = 1.
            return

        if assessments.puck_is_heading_to_me(env):
            basic_actions.turn_to_unit(env, env.world.puck)
            return

        speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        if env.me.get_distance_to_unit(self.defence_point) >= 20:
            experiments.fast_move_to_point(env, self.defence_point)
        elif speed_abs > 0.01:
            experiments.do_stop(env)
        else:
            basic_actions.turn_to_unit(env, env.world.puck)

