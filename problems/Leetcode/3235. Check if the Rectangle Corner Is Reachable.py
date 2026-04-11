# we need to know if a circle touches an edge (a line segment)
# say we are checking the circle against the top edge
# we cannot just check if the y coordinate of our center is in range of the top edge because our circle could be like way out to the left
# instead we want to find which point on the segment is closest to our circle and check the distance from that to our circle
# say our circle center is somewhere above the line (and not out to the side), obviously the point on the line directly below is closest
# if our circle is out to the side though, it's one of the end points of the line segment
def getTouches(cx, cy, r, xCorner, yCorner):
    touches = set()
    r2 = r * r
    clampX = max(0, min(cx, xCorner))
    clampY = max(0, min(cy, yCorner))
    if (cx - clampX) ** 2 + (cy - yCorner) ** 2 <= r2:
        touches.add("top")
    if (cx - clampX) ** 2 + cy ** 2 <= r2:
        touches.add("bottom")
    if cx ** 2 + (cy - clampY) ** 2 <= r2:
        touches.add("left")
    if (cx - xCorner) ** 2 + (cy - clampY) ** 2 <= r2:
        touches.add("right")
    return touches

def getIntersections(c1, c2):
    x1, y1, r1 = c1
    x2, y2, r2 = c2
    dx, dy = x2 - x1, y2 - y1
    distSq = dx * dx + dy * dy

    # if they are concentric we will just say there's no intersections for the purposes of this problem
    # since one contains another (or both are equal) it doesn't affect / make the pathing any worse
    if distSq == 0:
        return []

    # if the two circles don't touch at all, there's no intersection points
    if distSq > (r1 + r2) ** 2:
        return []

    dist = distSq ** 0.5

    # how far along the center-to-center line the chord sits
    chordMidDist = (r1 * r1 - r2 * r2 + distSq) / (2 * dist)

    # half the length of the chord (how far off to the side each point is)
    halfChordSq = r1 * r1 - chordMidDist * chordMidDist

    if halfChordSq < 0:
        return []

    halfChord = halfChordSq ** 0.5

    # midpoint of the chord
    midX = x1 + chordMidDist * dx / dist
    midY = y1 + chordMidDist * dy / dist

    # perpendicular offset direction
    perpX = -dy / dist * halfChord
    perpY = dx / dist * halfChord

    return [(midX + perpX, midY + perpY), (midX - perpX, midY - perpY)]

def intersectsInRect(c1, c2, xCorner, yCorner):
    for sx, sy in getIntersections(c1, c2):
        if 0 <= sx <= xCorner and 0 <= sy <= yCorner:
            return True
    return False

class DSU:
    def __init__(self, circles, xCorner, yCorner):
        self.parents = {i: i for i in range(len(circles))}
        self.sizes = {i: 1 for i in range(len(circles))}
        self.touches = {i: getTouches(circles[i][0], circles[i][1], circles[i][2], xCorner, yCorner) for i in range(len(circles))} # maps representative node to do we touch top edge, left edge, right edge, and bottom edge
    def find(self, node):
        if self.parents[node] != node:
            self.parents[node] = self.find(self.parents[node])
        return self.parents[node]
    def unite(self, a, b):
        pa = self.find(a)
        pb = self.find(b)
        if pa == pb:
            return False
        sa = self.sizes[pa]
        sb = self.sizes[pb]
        if sa <= sb:
            self.sizes[pb] += sa
            self.touches[pb] = self.touches[pb] | self.touches[pa]
            self.parents[pa] = pb
        else:
            self.sizes[pa] += sb
            self.touches[pa] = self.touches[pa] | self.touches[pb]
            self.parents[pb] = pa
        return True
class Solution:
    def canReachCorner(self, xCorner: int, yCorner: int, circles: List[List[int]]) -> bool:
        uf = DSU(circles, xCorner, yCorner)
        # union two touching circles
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                doesIntersectInRect = intersectsInRect(circles[i], circles[j], xCorner, yCorner)
                if not doesIntersectInRect:
                    continue
                uf.unite(i, j)
        
        for i in range(len(circles)):
            touches = uf.touches[uf.find(i)]
            if 'top' in touches and 'bottom' in touches:
                return False
            if 'top' in touches and 'right' in touches:
                return False
            if 'left' in touches and 'right' in touches:
                return False
            if 'left' in touches and 'bottom' in touches:
                return False
        
        return True

                
        