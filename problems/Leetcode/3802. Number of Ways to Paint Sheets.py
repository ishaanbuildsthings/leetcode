class Solution:
    def numberOfWays(self, n: int, limit: List[int]) -> int:
        MOD = 10**9 + 7
        limit.sort()
        pf = []
        curr = 0
        for v in limit:
            curr += v
            pf.append(curr)
        
        def query(l, r):
            return pf[r] - (pf[l - 1] if l else 0)
        
        contributeFullCount = 0
        for v in limit:
            if v >= n - 1:
                contributeFullCount += 1
        
        res = 0
        for i, v in enumerate(limit):
            maxReq = n - 1
            # if we use all of these, minimum we need of another color
            minReq = n - v
            minReq = max(minReq, 1)

            # at a minimum we must take minReq from another sheet
            # so any other sheet that doesn't even have that many can't contribute
            
            # at a maximum we must take n-1 from another sheet
            # anything that has >= n-1 sheets could contribute the full amount

            # we can take any amount 1...v and combine it with all others that can contribute full
            options = (min(v, n - 1) * (contributeFullCount - (1 if v >= (n - 1) else 0))) % MOD
            res = (res + options) % MOD

            # now we need things that have minReq...maxReq-1
            # these can contribute partial amounts based on how big they are

            # find leftmost index >= minReq
            l = 0
            r = len(limit) - 1
            leftI = None
            while l <= r:
                m = (r + l) // 2
                if limit[m] >= minReq:
                    leftI = m
                    r = m - 1
                else:
                    l = m + 1
            
            # find rightmost index <= maxReq-1
            l = 0
            r = len(limit) - 1
            rightI = None
            while l <= r:
                m = (r + l) // 2
                if limit[m] <= maxReq - 1:
                    rightI = m
                    l = m + 1
                else:
                    r = m - 1
            
            if leftI is None or rightI is None:
                continue
            
            tot = query(leftI, rightI)
            width = rightI - leftI + 1
            # exclude this from the partial to not count it against itself
            if minReq <= limit[i] <= maxReq - 1:
                tot -= limit[i]
                width -= 1

            tot -= width * (minReq - 1)
            res = (res + tot) % MOD
        
        return res

