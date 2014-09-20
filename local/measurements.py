import geometry
import prediction
import shortcuts
import experiments


def make_puck(env, x, y, speed_x=None, speed_y=None):
    goal_point = experiments.get_goal_point(env, puck=geometry.Point(x, y))
    if speed_x is None:
        speed_x = goal_point.x - x
        speed_y = goal_point.y - y
        norm = geometry.vector_abs(speed_x, speed_y)
        speed_x = speed_x * 17. / norm
        speed_y = speed_y * 17. / norm
    return prediction.UnitShadow(x, y, speed_x, speed_y)


def goalie_by_puck(env, puck):
    # HARDCODE
    goalie_radius = 30.
    min_goalie_y = env.game.goal_net_top + goalie_radius
    max_goalie_y = env.game.goal_net_top + env.game.goal_net_height - goalie_radius

    goalie_x = shortcuts.opponent_goalie(env).x
    goalie_y = max(min(max_goalie_y, puck.y), min_goalie_y)

    return prediction.UnitShadow(goalie_x, goalie_y, 0, 0)


def count_chances(env):
    radius = env.world.puck.radius
    total = 0
    hits = 0
    hits_in_area = 0
    hits_not_in_area = 0
    miss_in_area = 0
    miss_not_in_area = 0

    polygon = experiments.count_puck_attack_area(env, shortcuts.opponent_player(env))

    for x in range(int(env.game.rink_left + radius), int(env.game.rink_right - radius), 5):
        for y in range(int(env.game.rink_top + radius), int(env.game.rink_bottom - radius), 5):

            if y > shortcuts.rink_center(env).y:
                continue

            puck = make_puck(env, x, y)
            goalie = goalie_by_puck(env, puck)
            hit = not prediction.goalie_can_save_straight(
                env, puck=puck, goalie=goalie)

            in_area = geometry.point_in_convex_polygon(
                geometry.Point(x, y), polygon)

            total += 1
            if hit:
                hits += 1
            if hit and in_area:
                hits_in_area += 1
            if hit and not in_area:
                hits_not_in_area += 1
            if not hit and in_area:
                miss_in_area += 1
            if not hit and not in_area:
                miss_not_in_area += 1

    print 'total', total
    print 'hits', hits
    print 'hits_in_area', hits_in_area
    print 'hits_not_in_area', hits_not_in_area
    print 'miss_in_area', miss_in_area
    print 'miss_not_in_area', miss_not_in_area


def can_hit(env, x, y):
    puck = make_puck(env, x, y)
    goalie = goalie_by_puck(env, puck)
    return not prediction.goalie_can_save_straight(
        env, puck=puck, goalie=goalie)


def test(env):
    x, y = 950.975341797, 343.462585449
    speed_x, speed_y = 15.5862091064, 13.4079335531
    # x = shortcuts.opponent_player(env).net_front - env.game.goal_net_height
    # y = env.game.goal_net_top
    print 'start puck', x, y
    # puck = make_puck(env, x, y)
    puck = make_puck(env, x, y, speed_x, speed_y)
    goalie = goalie_by_puck(env, puck)
    return prediction.goalie_can_save_straight(
        env, puck=puck, goalie=goalie)
