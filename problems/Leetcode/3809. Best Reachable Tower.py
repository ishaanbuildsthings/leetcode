class Solution:
    def bestTower(self, towers: List[List[int]], center: List[int], radius: int) -> List[int]:
        resQ = -1
        res = [inf, inf]
        def dist(p1, p2):
            return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
        for x, y, q in towers:
            if q < resQ:
                continue
            d = dist(center, (x, y))
            if d > radius:
                continue
            if q > resQ:
                resQ = q
                res = [x, y]
            else:
                res = min(res, [x, y])
        if res == [inf, inf]:
            return [-1, -1]
        return res