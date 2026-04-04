class Solution:
    def numberOfBoomerangs(self, points: List[List[int]]) -> int:
        res = 0
        counts = defaultdict(lambda : defaultdict(int)) # counts[i][dist] tells us how many points are that distance
        for i in range(len(points)):
            for j in range(len(points)):
                if i == j: continue
                dx = abs(points[i][0] - points[j][0])
                dy = abs(points[i][1] - points[j][1])
                dist = dx * dx + dy * dy
                counts[i][dist] += 1
                
        res = 0
        for i in range(len(points)):
            for dist in counts[i]:
                opts = counts[i][dist]
                res += (opts * (opts - 1))
        
        return res