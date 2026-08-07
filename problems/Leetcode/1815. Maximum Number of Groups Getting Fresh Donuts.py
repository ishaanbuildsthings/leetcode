class Solution:
    def maxHappyGroups(self, batchSize: int, groups: List[int]) -> int:
        c = Counter(x % batchSize for x in groups)
        res = c[0]
        c[0] = 0
        for remainder in range(1, batchSize):
            mn = min(c[remainder], c[batchSize - remainder]) if remainder != batchSize - remainder else c[remainder] // 2
            res += mn
            c[remainder] -= mn
            c[batchSize - remainder] -= mn
                

        arr = [0] * batchSize
        for rem in range(batchSize):
            arr[rem] = c[rem]
        
        tup = tuple(arr)

        @cache
        def dp(tup, remainder):
            if max(tup) == 0:
                return 0
            res = 0
            for rem in range(len(tup)):
                if not tup[rem]:
                    continue
                nremainder = (rem + remainder) % batchSize
                didScore = remainder == 0
                ntup = list(tup)
                ntup[rem] -= 1
                ntup = tuple(ntup)
                nscore = int(didScore) + dp(ntup, nremainder)
                res = max(res, nscore)
            return res
        
        return dp(tup, 0) + res



