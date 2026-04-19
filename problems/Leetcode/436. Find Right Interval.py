class Solution:
    def findRightInterval(self, intervals: List[List[int]]) -> List[int]:
        res = [None] * len(intervals)

        dupe = intervals[:]
        for i in range(len(dupe)):
            dupe[i].append(i)
        dupe.sort() # holds (l, r, initial index)

        for i in range(len(intervals)):
            end = intervals[i][1]
            # find the smallest start in dupe that is >= end
            l = 0
            r = len(dupe) - 1
            resI = None
            while l <= r:
                m = (r+l)//2
                tup = dupe[m]
                tupStart = tup[0]
                if tupStart >= end:
                    resI = m
                    r = m - 1
                else:
                    l = m + 1
            if resI is None:
                res[i] = -1
                continue
            res[i] = dupe[resI][-1]
        
        return res