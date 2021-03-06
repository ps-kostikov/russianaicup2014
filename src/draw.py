import os


DRAW_FILE = 'draw'


def _append_line(line):
    content = ''
    try:
        with open(DRAW_FILE) as of:
            content = of.read()
    except:
        pass

    content += line
    content += '\n'

    with open(DRAW_FILE, 'w') as inf:
        inf.write(content)


def circle(point, radius):
    line = 'circle {0} {1} {2}'.format(point.x, point.y, radius)
    _append_line(line)


def line(p1, p2):
    line = 'line {0} {1} {2} {3}'.format(p1.x, p1.y, p2.x, p2.y)
    _append_line(line)


def cross(p, size=5):
    line1 = 'line {0} {1} {2} {3}'.format(p.x, p.y - size, p.x, p.y + size)
    _append_line(line1)
    line2 = 'line {0} {1} {2} {3}'.format(p.x - size, p.y, p.x + size, p.y)
    _append_line(line2)


def polygon(pol):
    next_points = [pol.points[-1]] + pol.points[:-1]
    for p1, p2 in zip(pol.points, next_points):
        line = 'line {0} {1} {2} {3}'.format(p1.x, p1.y, p2.x, p2.y)
        _append_line(line)


def point(p):
    line = 'point {0} {1}'.format(p.x, p.y)
    _append_line(line)
