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


def unit_in_sector(hockeyist, unit, max_distance, half_sector):
    angle = hockeyist.get_angle_to_unit(unit)
    distance = hockeyist.get_distance_to_unit(unit)
    return distance <= max_distance and abs(angle) <= half_sector


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.null_tick_prepare(env)

        self.save_start_game_tick(env)

        if env.me.state == HockeyistState.SWINGING:
            if self.swing_condition(env):
                env.move.action = ActionType.SWING

            if self.strike_condition(env):
                env.move.action = ActionType.STRIKE

            return

        hwp = shortcuts.hockeyist_with_puck(env)
        if hwp is None or hwp.player_id != env.me.player_id:
            self.defence_mode(env)
        else:
            self.attack_mode(env)

    def attack_mode(self, env):
        hwp = shortcuts.hockeyist_with_puck(env)
        if hwp.id == env.me.id:
            self.attack_with_puck(env)
        else:
            self.do_protect_goal_actions(env)

    def defence_mode(self, env):
        my_nearest_hockeyist = min(
            shortcuts.my_field_hockeyists(env),
            key=lambda h: assessments.ticks_to_reach_point(env, h, env.world.puck)
        )
        if my_nearest_hockeyist.id == env.me.id:
            self.do_get_puck_actions(env)
        else:
            self.do_protect_goal_actions(env)

    def null_tick_prepare(self, env):
        self.orders = {}
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

    def save_start_game_tick(self, env):
        puck = env.world.puck
        if geometry.distance(puck, shortcuts.rink_center(env)) > 0.1:
            return
        puck_abs_speed = geometry.vector_abs(puck.speed_x, puck.speed_y)
        if puck_abs_speed > 0.1:
            return
        self.game_start_tick = env.world.tick

    def strike_condition(self, env):
        if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
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

    def can_run(self, env):
        if abs(env.world.puck.y - shortcuts.rink_center(env).y) < 130:
            return False
        for oh in shortcuts.opponent_field_hockeyists(env):
            if geometry.distance(env.me, oh) < 150:
                return False
        return True

    def swing_condition(self, env):
        if self.can_run(env):
            return False
        puck = assessments.puck_after_strike(env)
        return not prediction.goalie_can_save_straight(env, puck=puck)

    def pass_condition(self, env, strike_point):
        if env.world.tick - self.game_start_tick <= 75:
            return True

        collega = filter(
            lambda h: h.id != env.me.id,
            shortcuts.my_field_hockeyists(env)
        )[0]
        net_center = shortcuts.net_front_center(env, shortcuts.opponent_player(env))
        if geometry.distance(collega, env.me) > 200:
            for oh in shortcuts.opponent_field_hockeyists(env):
                # my_angle = geometry.ray_ray_angle(env.me, strike_point, net_center)
                # o_angle = geometry.ray_ray_angle(oh, strike_point, net_center)
                # my_distance = geometry.distance(env.me, strike_point)
                # o_distance = geometry.distance(oh, strike_point)

                # if my_angle > o_angle and my_distance > o_distance:
                #     return True

                if geometry.interval_point_distance(env.me, strike_point, oh) < 60:
                    return True

        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.dead_polygons):
            return True

        return False

    def count_strike_point(self, env):
        hwp = shortcuts.hockeyist_with_puck(env)
        if hwp is None:
            return None

        def f(point):
            nfc = shortcuts.net_front_center(env, shortcuts.opponent_player(env))
            angles = [
                min(
                    geometry.degree_to_rad(110),
                    geometry.ray_ray_angle(oh, hwp, point)
                )
                for oh in shortcuts.opponent_field_hockeyists(env)
                if geometry.distance(oh, nfc) > 300
            ]
            ticks_to_reach_point = assessments.ticks_to_reach_point(env, hwp, point)
            if not angles:
                return -ticks_to_reach_point
            return geometry.rad_to_degree(min(angles)) - ticks_to_reach_point / 100

        return algorithm.best_point_for_polynoms(
            self.target_polygons, f=f)

    def attack_with_puck(self, env):
        strike_point = self.count_strike_point(env)

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

        experiments.fast_move_to_point_forward(env, strike_point)

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

        if hwp is not None and shortcuts.can_strike_unit(env, hwp):
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

