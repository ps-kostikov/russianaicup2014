import math
import collections

from model.ActionType import ActionType
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

import geometry


STRIKE_ANGLE = geometry.degree_to_rad(1.0)

Env = collections.namedtuple('Env', 'me world game move')
Point = collections.namedtuple('Point', 'x y')


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
    return Point(goal_x, goal_y)


def move_to_point(env, point):
    MIN_DIST = 40
    MEDIUM_DIST = 40
    MIN_ANGLE = math.pi / 4

    distance = env.me.get_distance_to_unit(point)
    angle = env.me.get_angle_to_unit(point)

    # already at point
    if distance < MIN_DIST:
        return False

    # faster to move forward
    if distance > MEDIUM_DIST:
        env.move.turn = angle
        if abs(angle) < MIN_ANGLE:
            env.move.speed_up = 1.

    # can reach poing forward or backward
    if -math.pi / 2. < angle < math.pi / 2.:
        env.move.turn = angle
        if -MIN_ANGLE < angle < MIN_ANGLE:
            env.move.speed_up = 1.
    else:
        env.move.turn = -angle
        if angle > math.pi - MIN_ANGLE or angle < -math.pi + MIN_ANGLE:
            env.move.speed_up = -1.

    return True


class MyStrategy:

    # LEFT_STRIKE_POINTS = [
    #     Point(212, 296.5),
    #     Point(212, 596.5),
    # ]
    LEFT_STRIKE_POINTS = [
        Point(212, 296.5),
        Point(212, 596.5),
    ]
    RIGHT_STRIKE_POINTS = [
        Point(812, 296.5),
        Point(812, 596.5),
    ]

    def move(self, me, world, game, move):

        env = Env(me, world, game, move)

        if attack_mode(env):
            self.do_attack_actions(env)
        else:
            self.do_defence_actions(env)

    def do_attack_actions(self, env):
        if env.me.state == HockeyistState.SWINGING:
            env.move.action = ActionType.STRIKE
            return

        if env.world.puck.owner_hockeyist_id == env.me.id:

            strike_point = self.get_nearest_strike_point(env)
            if move_to_point(env, strike_point):
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
            lambda h: h.type != HockeyistType.GOALIE and h.teammate,
            world.hockeyists)

        return min(*enemy_hockeyists, key=lambda h: h.get_distance_to(x, y))

    def get_nearest_strike_point(self, env):
        opponent_net_point = Point(
            env.world.get_opponent_player().net_top,
            env.world.get_opponent_player().net_left,
        )
        my_net_point = Point(
            env.world.get_my_player().net_top,
            env.world.get_my_player().net_left,
        )
        if (geometry.distance(self.LEFT_STRIKE_POINTS[0], opponent_net_point) <
                geometry.distance(self.LEFT_STRIKE_POINTS[0], my_net_point)):
            strike_points = self.LEFT_STRIKE_POINTS
        else:
            strike_points = self.RIGHT_STRIKE_POINTS


        return min(
            *strike_points,
            key=lambda p: env.me.get_distance_to_unit(p))
