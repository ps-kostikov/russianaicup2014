import prediction
import geometry
import shortcuts


def _count_player_weak_points(env, player):
    is_left = 1. if player.net_back < shortcuts.rink_center(env).x else -1.
    return [
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top - 50
        ),
        geometry.Point(
            player.net_front + is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top + env.game.goal_net_height + 50
        )
    ]


def count_strike_points(env):
    return _count_player_weak_points(
        env,
        shortcuts.opponent_player(env)
    )


def count_weak_points(env):
    return _count_player_weak_points(
        env,
        shortcuts.my_player(env)
    )


def count_defence_point(env):
    im_left = shortcuts.im_left(env)
    my_player = shortcuts.my_player(env)
    return geometry.Point(
        my_player.net_front + im_left * env.game.goal_net_height / 2.,
        shortcuts.field_center(env).y
    )


def fast_move_to_point(env, point):
    distance = env.me.get_distance_to_unit(point)
    mirrow_point = geometry.Point(
        2 * env.me.x - point.x,
        2 * env.me.y - point.y
    )
    time_turn_forward = abs(env.me.get_angle_to_unit(point)) / env.game.hockeyist_turn_angle_factor
    time_move_forward = prediction.count_n_by_x(
        0, 0, env.game.hockeyist_speed_up_factor, distance)

    time_turn_backward = abs(env.me.get_angle_to_unit(mirrow_point)) / env.game.hockeyist_turn_angle_factor
    time_move_backward = prediction.count_n_by_x(
        0, 0, env.game.hockeyist_speed_down_factor, distance)
    if time_turn_backward + time_move_backward > time_turn_forward + time_move_forward:
        fast_move_to_point_forward(env, point)
    else:
        fast_move_to_point_backward(env, point)


def fast_move_to_point_forward(env, point):
    distance = env.me.get_distance_to_unit(point)
    angle = env.me.get_angle_to_unit(point)

    if abs(angle) > geometry.degree_to_rad(1):
        env.move.turn = angle
        return

    v0 = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
    vn = 0
    a = -env.game.hockeyist_speed_down_factor
    n = prediction.count_n(v0, a, vn)

    if n is None:
        env.move.speed_up = 1.0
        return

    n = round(n) + 1
    x0 = 0.
    xn = prediction.count_xn(x0, v0, a, n)

    if xn > distance:
        env.move.speed_up = -1.0
    else:
        env.move.speed_up = 1.0


def fast_move_to_point_backward(env, point):
    distance = env.me.get_distance_to_unit(point)
    mirrow_point = geometry.Point(
        2 * env.me.x - point.x,
        2 * env.me.y - point.y
    )
    angle = env.me.get_angle_to_unit(mirrow_point)

    if abs(angle) > geometry.degree_to_rad(1):
        env.move.turn = angle
        return

    v0 = geometry.vector_abs(env.me.speed_x, env.me.speed_y)
    vn = 0
    a = -env.game.hockeyist_speed_up_factor
    n = prediction.count_n(v0, a, vn)

    if n is None:
        env.move.speed_up = -1.0
        return

    n = round(n) + 1
    x0 = 0.
    xn = prediction.count_xn(x0, v0, a, n)

    if xn > distance:
        env.move.speed_up = 1.0
    else:
        env.move.speed_up = -1.0


def get_goal_point(env):
    opponent_player = env.world.get_opponent_player()
    goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
    goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
    goal_y += (0.5 if env.me.y < goal_y else -0.5) * env.game.goal_net_height
    return geometry.Point(goal_x, goal_y)
