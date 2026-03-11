class Solution:
    def longestWPI(self, hours: List[int]) -> int:
        # O(n log n) solution 1
        # remap to +1 means tired and -1 means rested
        # for a given R we have some surplus, say +3 means 3 tired
        # we can cut off at most +2 from the left, and we want the leftmost one <= 2
        # so binary search for leftmost prefix with a min <= 2
        hours = [1 if x > 8 else -1 for x in hours]
        pfMin = []
        currSum = 0
        currMin = inf
        for v in hours:
            currSum += v
            currMin = min(currMin, currSum)
            pfMin.append(currMin)

        res = 0
        currSum = 0
        for right in range(len(hours)):
            currSum += hours[right]
            if currSum > 0:
                res = max(res, right + 1)
                continue

            # say we are at +5 meaning we are tired
            # we need to cut off at MOST +4 as a prefix, the leftmost possible that is >= to that
            maxCutOff = currSum - 1 # anything <= this is okay

            l = 0
            r = right - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                smallestPf = pfMin[m]
                if smallestPf <= maxCutOff:
                    resI = m
                    r = m - 1
                else:
                    l = m + 1
            if resI is not None:
                width = right - resI
                res = max(res, width)
                    
        return res



            