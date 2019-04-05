import math

def error(clusters):
    e = 0
    for c in clusters:
        for p in c.points:
            e += euclid_dist(p.lat, p.lon, c.lat, c.lon)**2
    return e

def euclid_dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def manhattan_dist(x1, y1, x2, y2):
    return math.fabs(x1 - x2) + math.fabs(y1 - y2)