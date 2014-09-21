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
            self.weak_polygons = experiments.count_optimistic_attack_polygons(
                env, mp)

            self.last_puck_owner_player_id = None

        self.save_last_puck_owner(env)

        if env.me.state == HockeyistState.SWINGING:
            if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
                env.move.action = ActionType.STRIKE
            elif assessments.someone_can_reach_me_after_ticks(env, 2):
                env.move.action = ActionType.STRIKE
            else:
                env.move.action = ActionType.SWING
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

    def attack_with_puck(self, env):

        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.attack_polygons):
            goal_point = experiments.get_goal_point(env)
            basic_actions.turn_to_unit(env, goal_point)

            if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
                env.move.action = ActionType.SWING
            return

        def count_target_polygons(env):
            res = []
            for p in self.target_polygons:
                my_dist = geometry.convex_polygon_point_distance(p, env.me)
                counted_opp_hs = []
                rad = (env.game.rink_bottom - env.game.rink_top) / 2.
                opp_net_center = shortcuts.net_front_center(env, shortcuts.opponent_player(env))
                for oh in shortcuts.opponent_field_hockeyists(env):
                    if geometry.distance(oh, opp_net_center) > rad:
                        counted_opp_hs.append(oh)

                if not counted_opp_hs:
                    res.append(p)
                    continue

                opp_dists = [
                    geometry.convex_polygon_point_distance(p, h)
                    for h in counted_opp_hs
                ]
                if my_dist < min(opp_dists):
                    res.append(p)

            if not res:
                return self.target_polygons
            return res

        def f(point):
            # s = 0
            # for oh in shortcuts.opponent_field_hockeyists(env):
            #     s -= 1. / (geometry.distance(oh, point) ** 2)
            return -assessments.ticks_to_reach_point(env, env.me, point)

        strike_point = algorithm.best_point_for_polynoms(
            count_target_polygons(env), f=f)

        collega = filter(
            lambda h: h.id != env.me.id,
            shortcuts.my_field_hockeyists(env)
        )[0]
        if geometry.distance(collega, env.me) > 200:
            for oh in shortcuts.opponent_field_hockeyists(env):
                if geometry.interval_point_distance(env.me, strike_point, oh) < 60:
                    # print 'me', env.me.x, env.me.y
                    # print 'strike_point', strike_point.x, strike_point.y
                    # print 'oh', oh.x, oh.y
                    self.do_pass(env)
                    return

        experiments.fast_move_to_point(env, strike_point)

    # def do_defence_actions(self, env):
    #     nearest_to_dp = shortcuts.nearest_unit(
    #         shortcuts.my_field_hockeyists(env), self.defence_point)
    #     if nearest_to_dp.id == env.me.id:
    #         self.do_protect_goal_actions(env)
    #     else:
    #         self.do_get_puck_actions(env)

    def its_dangerous(self, env):
        return any(geometry.point_in_convex_polygon(env.world.puck, p) for p in self.weak_polygons)
        # my_player = shortcuts.my_player(env)
        # my_goal_center = geometry.Point(
        #     my_player.net_front,
        #     (my_player.net_top + my_player.net_bottom) / 2.
        # )
        # return geometry.distance(env.world.puck, my_goal_center) < 400

    def do_get_puck_actions(self, env):
        if self.its_dangerous(env):
            hockeyist_with_puck = shortcuts.hockeyist_with_puck(env)
            if hockeyist_with_puck is not None:
                if shortcuts.can_strike_unit(env, hockeyist_with_puck):
                    env.move.action = ActionType.STRIKE
                    return

        env.move.speed_up = 1.0
        env.move.turn = env.me.get_angle_to_unit(env.world.puck)
        if shortcuts.can_take_puck(env):
            if self.last_puck_owner_player_id == env.me.player_id:
                env.move.action = ActionType.TAKE_PUCK
                return

            puck_abs_speed = geometry.vector_abs(env.world.puck.speed_x, env.world.puck.speed_y)
            if shortcuts.take_puck_probability(env, puck_abs_speed) >= 1.:
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

    def do_protect_goal_actions(self, env):
        if shortcuts.can_take_puck(env):
            if self.last_puck_owner_player_id == env.me.player_id:
                env.move.action = ActionType.TAKE_PUCK
                return

            puck_abs_speed = geometry.vector_abs(env.world.puck.speed_x, env.world.puck.speed_y)
            if shortcuts.take_puck_probability(env, puck_abs_speed) >= 0.95:
                env.move.action = ActionType.TAKE_PUCK
                return

        if shortcuts.can_strike_unit(env, env.world.puck):
            env.move.action = ActionType.STRIKE
            return

        if self.its_dangerous(env):
            basic_actions.turn_to_unit(env, env.world.puck)
            if basic_actions.turned_to_unit(env, env.world.puck):
                env.move.speed_up = 1.

        if env.me.get_distance_to_unit(self.defence_point) >= 10:
            experiments.fast_move_to_point(env, self.defence_point)

        speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        if speed_abs < 0.2:
            basic_actions.turn_to_unit(env, env.world.puck)

