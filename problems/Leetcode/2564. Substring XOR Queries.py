class Solution:
    def substringXorQueries(self, s: str, queries: List[List[int]]) -> List[List[int]]:
        LOG = 32
        earliest = defaultdict(lambda: (inf, inf)) # maps an int to the earliest left index it can occur at, and the size
        for windowSize in range(1, LOG + 1):
            if windowSize > len(s):
                break
            initString = s[:windowSize]
            initNum = int(initString, 2)
            currLeft, currSize = earliest[initNum]
            if windowSize < currSize:
                earliest[initNum] = (0, windowSize)
                
            l = 0
            r = windowSize - 1
            while r < len(s):
                r += 1
                if r == len(s):
                    break
                newEnd = s[r]
                lostEnd = s[l]
                # drop the left bit
                initNum &= (1 << (windowSize - 1)) - 1
                initNum <<= 1
                if newEnd == '1':
                    initNum += 1
                l += 1
                currentEarliestLeft, currentSize = earliest[initNum]
                if windowSize < currentSize:
                    earliest[initNum] = (l, windowSize)
        
        res = []
        for xorThis, target in queries:
            desired = xorThis ^ target
            if desired in earliest:
                left, size = earliest[desired]
                res.append([left, left + size - 1])
            else:
                res.append([-1,-1])
        return res


