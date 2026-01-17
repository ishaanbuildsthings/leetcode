class Solution:
    def isBoomerang(self, points: List[List[int]]) -> bool:
        def slope(p1, p2):
            if p2[0] == p1[0]:
                return inf
            return (p2[1] - p1[1]) / (p2[0] - p1[0])

        return len(set(tuple(p) for p in points)) == 3 and slope(points[1], points[2]) != slope(points[0], points[1])