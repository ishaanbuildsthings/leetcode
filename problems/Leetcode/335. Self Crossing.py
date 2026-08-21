# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# All ops O(1). Exact integer arithmetic; no floating point anywhere.
from fractions import Fraction

def cross(ox, oy, ax, ay, bx, by):
    return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

def sgn(x):
    return (x > 0) - (x < 0)

def onSegment(ax, ay, bx, by, px, py):
    return min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by)

def segmentsIntersect(a, b, c, d):
    # True iff CLOSED segments a-b and c-d share at least one point.
    # Endpoint touching and collinear overlap both count as True.
    # Zero-length segments (a == b) are handled correctly.
    ax, ay = a; bx, by = b; cx, cy = c; dx, dy = d
    d1 = sgn(cross(ax, ay, bx, by, cx, cy))
    d2 = sgn(cross(ax, ay, bx, by, dx, dy))
    d3 = sgn(cross(cx, cy, dx, dy, ax, ay))
    d4 = sgn(cross(cx, cy, dx, dy, bx, by))
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    if d1 == 0 and onSegment(ax, ay, bx, by, cx, cy):
        return True
    if d2 == 0 and onSegment(ax, ay, bx, by, dx, dy):
        return True
    if d3 == 0 and onSegment(cx, cy, dx, dy, ax, ay):
        return True
    if d4 == 0 and onSegment(cx, cy, dx, dy, bx, by):
        return True
    return False

def lineIntersection(a, b, c, d):
    # Crossing point of the INFINITE lines through a-b and c-d, as exact Fractions.
    # Returns None if parallel — including the identical-line case, which has
    # infinitely many intersections rather than none.
    ax, ay = a; bx, by = b; cx, cy = c; dx, dy = d
    rx, ry = bx - ax, by - ay
    sx, sy = dx - cx, dy - cy
    denom = rx * sy - ry * sx
    if denom == 0:
        return None
    t = Fraction((cx - ax) * sy - (cy - ay) * sx, denom)
    return (ax + t * rx, ay + t * ry)

class Solution:
    def isSelfCrossing(self, distance: List[int]) -> bool:
        q = deque() # going to hold the last 10 line segments

        x = y = 0
        DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        for i, v in enumerate(distance):
            dirI = i % 4
            dir = DIRS[dirI]
            nx = x + (dir[0] * v)
            ny = y + (dir[1] * v)
            # don't check the previous one, they will definitely touch at their shared point
            for j in range(len(q) - 1):
                px1, py1, px2, py2 = q[j]
                if segmentsIntersect((x, y), (nx, ny), (px1, py1), (px2, py2)):
                    return True
            q.append((x, y, nx, ny))
            if len(q) > 10:
                q.popleft()
            x = nx
            y = ny
        
        return False
            

