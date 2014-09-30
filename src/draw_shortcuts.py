import shortcuts
import draw
import geometry


def stick_circles(env):
    for h in shortcuts.my_field_hockeyists(env) + shortcuts.opponent_field_hockeyists(env):
        draw.circle(h, env.game.stick_length)


def stick_sectors(env):
    for h in shortcuts.my_field_hockeyists(env) + shortcuts.opponent_field_hockeyists(env):
        p1 = geometry.point_plus_vector(
            h, h.angle + env.game.stick_sector / 2., env.game.stick_length)
        p2 = geometry.point_plus_vector(
            h, h.angle - env.game.stick_sector / 2., env.game.stick_length)
        draw.line(h, p1)
        draw.line(h, p2)
