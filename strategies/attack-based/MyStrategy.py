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


STRIKE_ANGLE = geometry.degree_to_rad(1.0)


def get_nearest_hockeyist(world, unit):
    return min(
        *world.hockeyists,
        key=lambda h: h.get_distance_to_unit(unit))


def attack_mode(env):
    if env.world.puck.owner_player_id is not None:
        return env.world.puck.owner_player_id == env.me.player_id
    nearest_hockeyist = get_nearest_hockeyist(env.world, env.world.puck)
    return nearest_hockeyist.player_id == env.me.player_id


def get_goal_point(env):
    opponent_player = env.world.get_opponent_player()
    goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
    goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
    goal_y += (0.5 if env.me.y < goal_y else -0.5) * env.game.goal_net_height
    return geometry.Point(goal_x, goal_y)


class MyStrategy:

    def move(self, me, world, game, move):

        env = environment.Environment(me, world, game, move)

        if world.tick == 0:
            self.strike_points = experiments.count_strike_points(env)

        if env.me.state == HockeyistState.SWINGING:
            if env.me.swing_ticks >= env.game.max_effective_swing_ticks:
                env.move.action = ActionType.STRIKE
            else:
                env.move.action = ActionType.SWING
            return

        if attack_mode(env):
            self.do_attack_actions(env)
        else:
            self.do_defence_actions(env)

    def do_attack_actions(self, env):

        if env.world.puck.owner_hockeyist_id == env.me.id:

            strike_point = self.get_nearest_strike_point(env)

            if env.me.get_distance_to_unit(strike_point) >= 60:
                experiments.fast_move_to_point(env, strike_point)
                return

            goal_point = get_goal_point(env)
            angle_to_goal = env.me.get_angle_to_unit(goal_point)
            env.move.turn = angle_to_goal

            # if abs(angle_to_goal) < geometry.degree_to_rad(70):
            #     env.move.speed_up = 1.0

            if abs(angle_to_goal) < STRIKE_ANGLE:
                if env.me.get_distance_to_unit(goal_point) > env.world.width / 2.:
                    env.move.speed_up = 1.
                else:
                    env.move.action = ActionType.SWING
        else:
            nearest_opponent = self.get_nearest_opponent(env.me.x, env.me.y, env.world)
            if env.me.get_distance_to_unit(nearest_opponent) > env.game.stick_length:
                env.move.speed_up = 1.0
            elif abs(env.me.get_angle_to_unit(nearest_opponent)) < 0.5 * env.game.stick_sector:
                env.move.action = ActionType.STRIKE
            env.move.turn = env.me.get_angle_to_unit(nearest_opponent)

    def do_defence_actions(self, env):
        env.move.speed_up = 1.0
        env.move.turn = env.me.get_angle_to_unit(env.world.puck)
        env.move.action = ActionType.TAKE_PUCK

    def get_nearest_opponent(self, x, y, world):
        enemy_hockeyists = filter(
            lambda h: h.type != HockeyistType.GOALIE and not h.teammate,
            world.hockeyists)

        return min(*enemy_hockeyists, key=lambda h: h.get_distance_to(x, y))

    def get_nearest_strike_point(self, env):
        return min(
            *self.strike_points,
            key=lambda p: env.me.get_distance_to_unit(p))
