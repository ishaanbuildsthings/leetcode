# given two cricles (x1, y1, r1) and (x2, y2, r2) finds their intersection points in O(1)
# if they don't intersect, or are concentric or the same circle, returns no points
# otherwise returns two points (can be the same if they touch at one point)
# returns floats which could be imprecise
# it works by finding the chord across their intersection, finding a perpendicular line to it, and then finding those two points
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
