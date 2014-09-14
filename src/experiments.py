import prediction
import geometry
import shortcuts


def count_strike_points(env):
    opponent = shortcuts.opponent_player(env)
    opponent_is_left = 1. if opponent.net_back < shortcuts.rink_center(env).x else -1.
    return [
        geometry.Point(
            opponent.net_front + opponent_is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top - 50
        ),
        geometry.Point(
            opponent.net_front + opponent_is_left * env.game.goal_net_height * 1.5,
            env.game.goal_net_top + env.game.goal_net_height + 50
        )
    ]


def count_defence_point(env):
    im_left = shortcuts.im_left(env)
    my_player = shortcuts.my_player(env)
    return geometry.Point(
        my_player.net_front + im_left * env.game.goal_net_height / 2.,
        shortcuts.field_center(env).y
    )


def fast_move_to_point(env, point):
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


def get_goal_point(env):
    opponent_player = env.world.get_opponent_player()
    goal_x = 0.5 * (opponent_player.net_back + opponent_player.net_front)
    goal_y = 0.5 * (opponent_player.net_bottom + opponent_player.net_top)
    goal_y += (0.5 if env.me.y < goal_y else -0.5) * env.game.goal_net_height
    return geometry.Point(goal_x, goal_y)
