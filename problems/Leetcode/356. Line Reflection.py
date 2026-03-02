class Solution:
    def isReflected(self, points: List[List[int]]) -> bool:
        leftmostX = min(p[0] for p in points)
        rightmostX = max(p[0] for p in points)
        mid = (rightmostX+leftmostX) / 2
        c = Counter()
        for x, y in points:
            c[tuple([x, y])] += 1
        
        for x, y in points:

            dist = abs(mid - x)
            if x <= mid:
                refX = mid + dist
            else:
                refX = mid - dist
            
            t2 = tuple([refX, y])
            if c[t2] == 0:
                return False
        
        return True