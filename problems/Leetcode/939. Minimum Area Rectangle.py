class Solution:
    def minAreaRect(self, points: List[List[int]]) -> int:
        res = inf
        c = Counter(tuple(p) for p in points)
        for i in range(len(points)):
            x1, y1 = points[i]
            for j in range(i + 1, len(points)):
                x2, y2 = points[j]
                if x1 == x2 or y1 == y2:
                    continue
                p1 = (x1, y2)
                p2 = (x2, y1)
                if c[p1] and c[p2]:
                    area = abs(x1-x2) * abs(y1-y2)
                    res = min(res, area)
        return res if res != inf else 0
                
