class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        vals = []
        for i, lst in enumerate(nums):
            for v in lst:
                vals.append((v, i))
        vals.sort()
        
        res = [-inf, inf]
        l = r = 0
        n = len(vals)
        c = Counter() # count for each list how many values do we have
        while r < n:
            gainV, lstI = vals[r]
            c[lstI] += 1
            # while valid
            while len(c) == len(nums):
                rangeHere = [vals[l][0], vals[r][0]]
                width = rangeHere[1] - rangeHere[0]
                if width < res[1] - res[0]:
                    res = rangeHere[:]
                lostV, lostI = vals[l]
                c[lostI] -= 1
                if not c[lostI]: del c[lostI]
                l += 1
            r += 1
        return res

