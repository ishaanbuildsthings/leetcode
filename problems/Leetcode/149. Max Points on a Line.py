class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        def slope(p1, p2):
            rise = p2[1]-p1[1]
            run = p2[0]-p1[0]
            return rise / run if run != 0 else inf

        if len(points) <= 2:
            return len(points)

        
        res = 0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                resWithThese2 = 2
                slopeJToI = slope(points[j], points[i])
                for k in range(j + 1, len(points)):
                    slopeKToI = slope(points[k], points[i])
                    if abs(slopeKToI-slopeJToI) == 0 or slopeJToI == inf == slopeKToI:
                        resWithThese2 += 1
                res = max(res, resWithThese2)
        return res
