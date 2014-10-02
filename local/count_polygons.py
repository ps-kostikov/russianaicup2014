import shortcuts
import environment
import geometry
import measurements
import prediction

import shapely.geometry
import pickle


def make_start_env_im_left():
    with open('local/start_env_im_left.pickle') as inf:
        return pickle.load(inf)


def get_goal_point(env, puck, shift):
    opponent_player = env.world.get_opponent_player()
    if opponent_player.net_back > shortcuts.rink_center(env).x:
        goal_x = opponent_player.net_front + shift
    else:
        goal_x = opponent_player.net_front - shift
    if puck.y < shortcuts.rink_center(env):
        goal_y = opponent_player.net_bottom
    else:
        goal_y = opponent_player.net_top
    return geometry.Point(goal_x, goal_y)


def make_puck(env, x, y, speed_abs, shift):
    goal_point = get_goal_point(env, puck=geometry.Point(x, y), shift=shift)
    speed_x = goal_point.x - x
    speed_y = goal_point.y - y
    norm = geometry.vector_abs(speed_x, speed_y)
    speed_x = speed_x * speed_abs / norm
    speed_y = speed_y * speed_abs / norm
    return prediction.UnitShadow(x, y, speed_x, speed_y, 0)


def goalie_by_puck(env, puck):
    # HARDCODE
    goalie_radius = 30.
    min_goalie_y = env.game.goal_net_top + goalie_radius
    max_goalie_y = env.game.goal_net_top + env.game.goal_net_height - goalie_radius

    goalie_x = shortcuts.opponent_goalie(env).x
    goalie_y = max(min(max_goalie_y, puck.y), min_goalie_y)

    return prediction.UnitShadow(goalie_x, goalie_y, 0, 0, 0)


def find_points(env, speed_abs, shift):

    # polygon = experiments.count_puck_attack_area(env, shortcuts.opponent_player(env))
    step = 5
    res_str = ''
    points = []
    for x in range(int(env.game.rink_left), int(env.game.rink_right), step):
        for y in range(int(env.game.rink_top), int(env.game.rink_bottom), step):

            if y > shortcuts.rink_center(env).y:
                continue

            puck = make_puck(env, x, y, speed_abs, shift)
            goalie = goalie_by_puck(env, puck)
            hit = not prediction.goalie_can_save_straight(
                env, puck=puck, goalie=goalie)

            if hit:
                res_str += 'point {0} {1}\n'.format(x, y)
                points.append(geometry.Point(x, y))

            # if hit and x > 1100:
            #     import ipdb; ipdb.set_trace()
            #     pass

    if not points:
        return None

    hull = shapely.geometry.MultiPoint([
        shapely.geometry.Point(p.x, p.y)
        for p in points
    ]).convex_hull

    if hull.type != 'Polygon':
        return None

    pol = geometry.Polygon([
        geometry.Point(c[0], c[1])
        for c in list(hull.exterior.coords)
    ])
    return pol

    # next_points = [pol.points[-1]] + pol.points[:-1]
    # lines = []
    # for p1, p2 in zip(pol.points, next_points):
    #     line = 'line {0} {1} {2} {3}'.format(p1.x, p1.y, p2.x, p2.y)
    #     lines.append(line)
    # with open('draw_area', 'w') as i:
    #     i.write(res_str + '\n'.join(lines))


env = make_start_env_im_left()

pols = {}
optimistic_pols = {}
speed_abs = 15.
while speed_abs <= 20.:
    fp = find_points(env, speed_abs, 20)
    if fp is not None:
        pols[speed_abs] = fp
    fpo = find_points(env, speed_abs, 2)
    if fpo is not None:
        optimistic_pols[speed_abs] = fpo
    speed_abs += 0.5

up_right_pols = pols
rc = shortcuts.rink_center(env)

up_left_pols = {}
for k, v in up_right_pols.iteritems():
    up_left_pols[k] = geometry.Polygon([
        geometry.mirror_x(p, rc.x)
        for p in v.points
    ])

down_left_pols = {}
for k, v in up_right_pols.iteritems():
    down_left_pols[k] = geometry.Polygon([
        geometry.mirror_y(geometry.mirror_x(p, rc.x), rc.y)
        for p in v.points
    ])

down_right_pols = {}
for k, v in up_right_pols.iteritems():
    down_right_pols[k] = geometry.Polygon([
        geometry.mirror_y(p, rc.y)
        for p in v.points
    ])


optimistic_up_right_pols = optimistic_pols
rc = shortcuts.rink_center(env)

optimistic_up_left_pols = {}
for k, v in optimistic_up_right_pols.iteritems():
    optimistic_up_left_pols[k] = geometry.Polygon([
        geometry.mirror_x(p, rc.x)
        for p in v.points
    ])

optimistic_down_left_pols = {}
for k, v in optimistic_up_right_pols.iteritems():
    optimistic_down_left_pols[k] = geometry.Polygon([
        geometry.mirror_y(geometry.mirror_x(p, rc.x), rc.y)
        for p in v.points
    ])

optimistic_down_right_pols = {}
for k, v in optimistic_up_right_pols.iteritems():
    optimistic_down_right_pols[k] = geometry.Polygon([
        geometry.mirror_y(p, rc.y)
        for p in v.points
    ])


text = """
import geometry

"""
for name, pols in (
    ("up_right_pols", up_right_pols),
    ("up_left_pols", up_left_pols),
    ("down_left_pols", down_left_pols),
    ("down_right_pols", down_right_pols),
    ("optimistic_up_right_pols", optimistic_up_right_pols),
    ("optimistic_up_left_pols", optimistic_up_left_pols),
    ("optimistic_down_left_pols", optimistic_down_left_pols),
    ("optimistic_down_right_pols", optimistic_down_right_pols)
):
    text += """
{0} = {{
""".format(name)

    for k, p in pols.iteritems():
        text += """
    {0}: geometry.Polygon([
""".format(k)

        for point in p.points:
            text += """
        geometry.Point({0}, {1}),
""".format(point.x, point.y)
        text += """
    ]),
"""
    text += """
}

"""

with open('src/target_polygons.py', 'w') as out:
    out.write(text)

