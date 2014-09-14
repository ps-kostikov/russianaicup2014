import math


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


