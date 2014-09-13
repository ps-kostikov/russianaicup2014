from model.ActionType import ActionType

import geometry

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


class TurnToPoint(Action):
    def __init__(self, point):
        super(TurnToPoint, self).__init__()
        self.point = point

    def do(self, env):
        angle = env.me.get_angle_to_unit(self.point)
        if abs(angle) <= geometry.degree_to_rad(1):
            self.done = True
            return

        env.move.turn = angle


class MoveToPoint(Action):

    def __init__(self, point):
        super(MoveToPoint, self).__init__()
        self.point = point

    def do(self, env):
        distance = env.me.get_distance_to_unit(self.point)
        angle = env.me.get_angle_to_unit(self.point)

        if distance < 10:
            self.done = True
            return

        if abs(angle) > geometry.degree_to_rad(1):
            env.move.turn = angle
            return

        env.move.speed_up = 1.0


class TakePuck(Action):

    def do(self, env):
        if env.world.puck.owner_hockeyist_id == env.me.id:
            self.done = True
            return

        if can_take_puck(env):
            env.move.action = ActionType.TAKE_PUCK
        else:
            MoveToPoint(env.world.puck).do(env)


class Stop(Action):

    def do(self, env):
        speed_abs = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
        if speed_abs < 0.001:
            print 'stop done, tick = ', env.world.tick
            self.done = True
            return

        angle = geometry.get_angle(
            math.cos(env.me.angle), math.sin(env.me.angle),
            env.me.speed_x, env.me.speed_y)
        if abs(geometry.rad_to_degree(angle)) < 90:
            env.move.speed_up = -min(1., speed_abs / env.game.hockeyist_speed_down_factor)
        else:
            env.move.speed_up = min(1., speed_abs / env.game.hockeyist_speed_up_factor)


class Strike(Action):
    def __init__(self, delay=0):
        super(Strike, self).__init__()
        self.delay = delay
        self.start_tick = None

    def do(self, env):
        if self.start_tick is None:
            self.start_tick = env.world.tick

        if not self.delay or env.world.tick - self.start_tick >= self.delay:
            env.move.action = ActionType.STRIKE
            self.done = True
            return

        env.move.action = ActionType.SWING