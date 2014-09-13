from model.ActionType import ActionType

import geometry
import prediction

import math


def can_take_puck(env):
    distance = env.me.get_distance_to_unit(env.world.puck)
    angle = env.me.get_angle_to_unit(env.world.puck)

    return distance < env.game.stick_length and abs(angle) < 0.5 * env.game.stick_sector


class Action(object):
    def __init__(self):
        self.done = False


class ActionList:
    def __init__(self, *actions):
        self.actions = actions

    def do(self, env):
        to_do = filter(lambda a: not a.done, self.actions)
        if to_do:
            to_do[0].do(env)
            return True
        return False


class WaitForTick(Action):
    def __init__(self, tick):
        super(WaitForTick, self).__init__()
        self.tick = tick

    def do(self, env):
        if env.world.tick >= self.tick:
            self.done = True
            print 'tick = ', env.world.tick, 'WaitForTick done'


class TurnToPoint(Action):
    def __init__(self, point):
        super(TurnToPoint, self).__init__()
        self.point = point

    def do(self, env):
        angle = env.me.get_angle_to_unit(self.point)
        if abs(angle) <= geometry.degree_to_rad(0.1):
            self.done = True
            print 'tick = ', env.world.tick, 'TurnToPoint done'
            return

        env.move.turn = angle


class TurnToGoal(Action):
    def get_goal_point(self, env):
        opponent_player = env.world.get_opponent_player()
        goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
        goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
        goal_y += 0.5 * env.game.goal_net_height
        # print 'goal x = ', goal_x, 'goal_y = ', goal_y
        return geometry.Point(goal_x, goal_y)

    def do(self, env):
        point = self.get_goal_point(env)
        angle = env.me.get_angle_to_unit(point)
        if abs(angle) <= geometry.degree_to_rad(0.1):
            self.done = True
            print 'tick = ', env.world.tick, 'TurnToPoint done'
            return

        env.move.turn = angle


class MoveToPoint(Action):

    def __init__(self, point):
        super(MoveToPoint, self).__init__()
        self.point = point

    def do(self, env):
        distance = env.me.get_distance_to_unit(self.point)
        angle = env.me.get_angle_to_unit(self.point)

        if distance < 2:
            self.done = True
            speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
            print (
                'tick = ', env.world.tick,
                'MoveToPoint done',
                'x = ', env.me.x,
                'y = ', env.me.y,
                'speed abs = ', speed_abs
            )
            return

        if abs(angle) > geometry.degree_to_rad(1):
            env.move.turn = angle
            return

        v0 = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        vn = 0
        a = -env.game.hockeyist_speed_down_factor
        n = prediction.count_n(v0, a, vn)

        if n is None:
            env.move.speed_up = 1.0
            # print 'tick = ', env.world.tick, 'speed = 1. n is None'
            return

        n = round(n) + 1
        x0 = 0.
        xn = prediction.count_xn(x0, v0, a, n)

        # print (
        #     'v0 = ', v0,
        #     'n =', n,
        #     'xn =', xn,
        #     'dist = ', distance
        # )
        # import ipdb; ipdb.set_trace()
        if xn > distance:
            # print 'tick = ', env.world.tick, 'speed = -1.'
            env.move.speed_up = -1.0
        else:
            # print 'tick = ', env.world.tick, 'speed = 1.'
            env.move.speed_up = 1.0


class TakePuck(Action):

    def do(self, env):
        if env.world.puck.owner_hockeyist_id == env.me.id:
            self.done = True
            print 'tick = ', env.world.tick, 'TakePuck done'
            return

        if can_take_puck(env):
            env.move.action = ActionType.TAKE_PUCK
        else:
            MoveToPoint(env.world.puck).do(env)


class Stop(Action):

    def do(self, env):
        speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        if speed_abs < 0.0001:
            self.done = True
            print (
                'tick = ', env.world.tick,
                'Stop done',
                'x = ', env.me.x,
                'y = ', env.me.y,
                'speed abs = ', speed_abs
            )
            return

        angle = geometry.get_angle(
            math.cos(env.me.angle), math.sin(env.me.angle),
            env.me.speed_x, env.me.speed_y)
        if abs(geometry.rad_to_degree(angle)) < 90:
            env.move.turn = angle
            env.move.speed_up = -min(1., speed_abs / env.game.hockeyist_speed_down_factor)
        else:
            env.move.turn = -angle
            env.move.speed_up = min(1., speed_abs / env.game.hockeyist_speed_up_factor)


class Strike(Action):
    def __init__(self, delay=0):
        super(Strike, self).__init__()
        self.delay = delay
        self.start_tick = None

    def do(self, env):
        if env.me.remaining_cooldown_ticks:
            return

        if not self.delay or (self.start_tick is not None and env.world.tick - self.start_tick >= self.delay):
            env.move.action = ActionType.STRIKE
            self.done = True
            print 'tick = ', env.world.tick, 'Strike done'
            return

        env.move.action = ActionType.SWING
        if self.start_tick is None:
            self.start_tick = env.world.tick
