import geometry


def turn_to_unit(env, unit):
    angle = env.me.get_angle_to_unit(unit)
    env.move.turn = angle


def turned_to_unit(env, unit, eps=geometry.degree_to_rad(1)):
    angle = env.me.get_angle_to_unit(unit)
    return abs(angle) < eps
