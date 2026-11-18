# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/geometry/polygonArea.py

# Twice the signed area of a polygon (shoelace formula), as an exact integer for integer corners: the area is
# abs(result) / 2, and the sign is the direction, > 0 counterclockwise, < 0 clockwise, 0 for no area (e.g. all
# corners on one line). Doubling keeps it exact: integer corners always give a whole number or a whole and a half.
# points: the corners in order around the boundary (either direction, not shuffled), as (x, y) pairs; the last corner
# joins back to the first. Fewer than 3 corners give 0.
# polygonArea2([(0, 0), (4, 0), (4, 3)]) -> 12 (area 6, counterclockwise)
# O(n)
def polygonArea2(points):
    n = len(points)
    total = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[i + 1 - n]  # (the last corner joins back to the first)
        total += x1 * y2 - x2 * y1
    return total
