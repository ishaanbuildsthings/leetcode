class Solution:
    def findMaximalUncoveredRanges(self, n: int, ranges: List[List[int]]) -> List[List[int]]:
        ranges.sort()
    
        def merge(i):
            if not i:
                return i
            i.sort()
            prevStart = i[0][0]
            prevBig = i[0][1]
            res = []
            for j in range(1, len(i)):
                start, end = i[j]
                if start <= prevBig:
                    prevBig = max(prevBig, end)
                else:
                    res.append([prevStart, prevBig])
                    prevStart, prevBig = i[j]
            res.append([prevStart, prevBig])
            return res
        
        merged = merge(ranges)

        if not merged:
            return [[0, n - 1]]

        print(merged)

        res = []
        if merged[0][0] > 0:
            res.append([0, merged[0][0] - 1])
        for i in range(len(merged) - 1):
            l1, r1 = merged[i]
            l2, r2 = merged[i + 1]
            gap = l2 - r1
            if gap > 1:
                res.append([r1 + 1, l2 - 1])
        if merged[-1][1] < n - 1:
            res.append([merged[-1][1] + 1, n - 1])
        
            
        return res
        
        