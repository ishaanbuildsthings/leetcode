class Solution:
    def nearestValidPoint(self, x: int, y: int, points: List[List[int]]) -> int:
        resI = None
        resDist = inf
        for i, (x1, y1) in enumerate(points):
            if x1 != x and y1 != y:
                continue
            manhattan = abs(x - x1) + abs(y - y1)
            if manhattan < resDist:
                resI = i
                resDist = manhattan
        return resI if resI != None else -1