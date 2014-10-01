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
import draw


class Precount(object):
    def __init__(self, env):
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


class History(object):
    def __init__(self):
        self.game_start_tick = None


class GStrategy(object):
    def __init__(self, env, precount, history):
        self.precount = precount
        self.history = history

        # global aims
        self.do_pass = False
        self.do_goal = False
        self.do_get_puck = False

        # roles
        self.pass_taker = None
        self.pass_maker = None

        self.attacker = None
        self.defenceman = None
        self.attack_supporter = None

        self.active_puck_taker = None
        self.second_puck_taker = None


        self.strike_point = None
        self.hwp = shortcuts.hockeyist_with_puck(env)

    def count_strike_point(self, env):
        def f(point):
            nfc = shortcuts.net_front_center(env, shortcuts.opponent_player(env))
            angles = [
                min(
                    geometry.degree_to_rad(110),
                    geometry.ray_ray_angle(oh, self.hwp, point)
                )
                for oh in shortcuts.opponent_field_hockeyists(env)
                if geometry.distance(oh, nfc) > 300
            ]
            ticks_to_reach_point = assessments.ticks_to_reach_point(env, self.hwp, point)
            if not angles:
                return -ticks_to_reach_point
            return geometry.rad_to_degree(min(angles)) - ticks_to_reach_point / 100

        return algorithm.best_point_for_polynoms(
            self.precount.target_polygons, f=f)


class GStrategy2(GStrategy):
    def __init__(self, env, precount, history):
        super(GStrategy2, self).__init__(env, precount, history)

        my_nearest_hockeyist = min(
            shortcuts.my_field_hockeyists(env),
            key=lambda h: assessments.ticks_to_reach_point(env, h, env.world.puck)
        )
        my_other_hockeyist = filter(
            lambda h: h.id != my_nearest_hockeyist.id,
            shortcuts.my_field_hockeyists(env)
        )[0]
        if self.hwp is None or self.hwp.player_id != env.me.player_id:
            self.do_get_puck = True
            self.defenceman = my_other_hockeyist
            self.active_puck_taker = my_nearest_hockeyist
        else:
            self.strike_point = self.count_strike_point(env)
            if self.pass_condition(env, self.strike_point):
                self.do_pass = True
                self.pass_maker = self.hwp
                self.pass_taker = filter(
                    lambda h: h.id != self.hwp.id,
                    shortcuts.my_field_hockeyists(env)
                )[0]
            else:
                self.do_goal = True
                self.attacker = self.hwp
                self.defenceman = filter(
                    lambda h: h.id != self.hwp.id,
                    shortcuts.my_field_hockeyists(env)
                )[0]

    def pass_condition(self, env, strike_point):
        if env.world.tick - self.history.game_start_tick <= 75:
            return True

        h1, h2 = shortcuts.my_field_hockeyists(env)
        if geometry.distance(h1, h2) > 200:
            for oh in shortcuts.opponent_field_hockeyists(env):
                if geometry.interval_point_distance(self.hwp, strike_point, oh) < 60:
                    return True

        if any(geometry.point_in_convex_polygon(self.hwp, p) for p in self.precount.dead_polygons):
            return True

        return False


class GStrategy3(GStrategy):
    def __init__(self, env, precount, history):
        super(GStrategy3, self).__init__(env, precount, history)

        if self.hwp is None or self.hwp.player_id != env.me.player_id:
            self.do_get_puck = True
            puck_nearest_hockeyist = min(
                shortcuts.my_field_hockeyists(env),
                key=lambda h: assessments.ticks_to_reach_point(env, h, env.world.puck)
            )
            self.active_puck_taker = puck_nearest_hockeyist
            def_nearest_hockeyist = min(
                filter(
                    lambda h: h.id != puck_nearest_hockeyist.id,
                    shortcuts.my_field_hockeyists(env)
                ),
                key=lambda h: assessments.ticks_to_reach_point(env, h, self.precount.defence_point)
            )
            self.defenceman = def_nearest_hockeyist
            other_hockeyist = filter(
                lambda h: h.id not in (def_nearest_hockeyist.id, puck_nearest_hockeyist.id),
                shortcuts.my_field_hockeyists(env)
            )[0]
            self.second_puck_taker = other_hockeyist
        else:
            self.strike_point = self.count_strike_point(env)
            if self.pass_condition(env, self.strike_point):
                self.do_pass = True
                self.pass_maker = self.hwp
                self.pass_taker = self.count_pass_taker(env)
                other = filter(
                    lambda h: h.id not in (self.pass_maker.id, self.pass_taker.id),
                    shortcuts.my_field_hockeyists(env)
                )[0]
                def_nearest_hockeyist = min(
                    filter(
                        lambda h: h.id != self.hwp.id,
                        shortcuts.my_field_hockeyists(env)
                    ),
                    key=lambda h: assessments.ticks_to_reach_point(env, h, self.precount.defence_point)
                )
                if other.id == def_nearest_hockeyist.id:
                    self.defenceman = other
                else:
                    self.attack_supporter = other
            else:
                self.do_goal = True
                self.attacker = self.hwp
                self.defenceman = min(
                    filter(
                        lambda h: h.id != self.attacker.id,
                        shortcuts.my_field_hockeyists(env)
                    ),
                    key=lambda h: assessments.ticks_to_reach_point(env, h, self.precount.defence_point)
                )
                other = filter(
                    lambda h: h.id not in (self.attacker.id, self.defenceman.id),
                    shortcuts.my_field_hockeyists(env)
                )[0]
                self.attack_supporter = other

    def count_pass_taker(self, env):
        def f(h):
            return min(
                geometry.distance(h, oh)
                for oh in shortcuts.opponent_field_hockeyists(env)
            )
        if self.hwp is None or self.hwp.player_id != env.me.player_id:
            return None
        res = max(
            filter(
                lambda h: h.id != self.hwp.id,
                shortcuts.my_field_hockeyists(env)
            ),
            key=lambda h: f(h)
        )
        return res

    def pass_condition(self, env, strike_point):
        if env.world.tick - self.history.game_start_tick <= 75:
            return True

        pass_taker = self.count_pass_taker(env)
        if geometry.distance(self.hwp, pass_taker) > 200:
            for oh in shortcuts.opponent_field_hockeyists(env):
                if geometry.interval_point_distance(self.hwp, strike_point, oh) < 60:
                    return True

        if any(geometry.point_in_convex_polygon(self.hwp, p) for p in self.precount.dead_polygons):
            return True

        return False


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            if env.me.teammate_index == 0:
                print 'random seed', env.game.random_seed
            self.precount = Precount(env)
            self.history = History()

        self.save_start_game_tick(env)
        self.hwp = shortcuts.hockeyist_with_puck(env)
        if shortcuts.team_size(env) == 2:
            gstrategy = GStrategy2(env, self.precount, self.history)
        else:
            gstrategy = GStrategy3(env, self.precount, self.history)

        # FIXME move somewhere else
        if env.me.state == HockeyistState.SWINGING:
            if self.swing_condition(env):
                env.move.action = ActionType.SWING

            if self.strike_condition(env):
                env.move.action = ActionType.STRIKE

            return

        def match(role):
            return role is not None and role.id == env.me.id

        if gstrategy.do_goal:
            if match(gstrategy.attacker):
                self.attack_with_puck(env, gstrategy)
            elif match(gstrategy.defenceman):
                self.do_protect_goal_actions(env, gstrategy)
            elif match(gstrategy.attack_supporter):
                self.attack_without_puck(env, gstrategy)
            else:
                raise RuntimeError("no role defined for goal strategy")
        elif gstrategy.do_pass:
            if match(gstrategy.pass_taker):
                self.take_pass(env, gstrategy)
            elif match(gstrategy.pass_maker):
                self.do_pass(env, gstrategy)
            elif match(gstrategy.defenceman):
                self.do_protect_goal_actions(env, gstrategy)
            elif match(gstrategy.attack_supporter):
                self.attack_without_puck(env, gstrategy)
            else:
                raise RuntimeError('no role defined for pass strategy')
        elif gstrategy.do_get_puck:
            if match(gstrategy.defenceman):
                self.do_protect_goal_actions(env, gstrategy)
            elif match(gstrategy.active_puck_taker):
                self.do_get_puck_actions(env, gstrategy)
            elif match(gstrategy.second_puck_taker):
                self.do_get_puck_actions(env, gstrategy)
            else:
                raise RuntimeError('no role defined for get puck strategy')
        else:
            raise RuntimeError('no global strategy defined')

    def save_start_game_tick(self, env):
        puck = env.world.puck
        if geometry.distance(puck, shortcuts.rink_center(env)) > 0.1:
            return
        puck_abs_speed = geometry.vector_abs(puck.speed_x, puck.speed_y)
        if puck_abs_speed > 0.1:
            return
        self.history.game_start_tick = env.world.tick

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

    def attack_with_puck(self, env, gstrategy):
        strike_point = gstrategy.strike_point

        if any(geometry.point_in_convex_polygon(env.me, p) for p in self.precount.attack_polygons):
            goal_point = experiments.get_goal_point(env)
            basic_actions.turn_to_unit(env, goal_point)

            if basic_actions.turned_to_unit(env, goal_point, eps=geometry.degree_to_rad(1.0)):
                env.move.speed_up = 1.

            if self.swing_condition(env):
                env.move.action = ActionType.SWING

            if self.strike_condition(env):
                env.move.action = ActionType.STRIKE
            return

        experiments.fast_move_to_point_forward(env, strike_point)

    def attack_without_puck(self, env, gstrategy):
        strike_point = gstrategy.strike_point
        strike_point = geometry.mirror_x(strike_point, shortcuts.rink_center(env).x)
        strike_point = geometry.mirror_y(strike_point, shortcuts.rink_center(env).y)
        experiments.fast_move_to_point_forward(env, strike_point)

    def its_dangerous(self, env):
        return (any(geometry.point_in_convex_polygon(env.world.puck, p) for p in self.precount.weak_polygons)
            or geometry.distance(env.world.puck, self.precount.defence_point) < 120)

    def do_get_puck_actions(self, env, gstrategy):
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

    def do_pass(self, env, gstrategy):
        collega = gstrategy.pass_taker
        angle = env.me.get_angle_to_unit(collega)
        env.move.turn = angle
        if abs(angle) <= env.game.pass_sector / 2.:
            env.move.action = ActionType.PASS
            env.move.pass_angle = angle
            env.move.pass_power = 0.8

    def take_pass(self, env, gstrategy):
        basic_actions.turn_to_unit(env, env.world.puck)

    def do_protect_goal_actions(self, env, gstrategy):
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

        if self.its_dangerous(env) and env.me.get_distance_to_unit(self.precount.defence_point) < 100:
            basic_actions.turn_to_unit(env, env.world.puck)
            if geometry.distance(self.precount.defence_point, env.world.puck) <= 200:
                if basic_actions.turned_to_unit(env, env.world.puck):
                    env.move.speed_up = 1.
            return

        speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        if env.me.get_distance_to_unit(self.precount.defence_point) >= 20:
            experiments.fast_move_to_point(env, self.precount.defence_point)
        elif speed_abs > 0.01:
            experiments.do_stop(env)
        else:
            basic_actions.turn_to_unit(env, env.world.puck)

