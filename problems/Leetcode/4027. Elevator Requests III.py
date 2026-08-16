class Solution:
    def elevatorRequests(self, n: int, start: int, requests: list[list[int]]) -> int:
        # 2^16 = 64,000
        # 16 for the current floor we are on
        # another 16 to loop over where to go next

        M = len(requests)
        fmask = (1 << M) - 1

        # min time to have reached this mask state
        
        @cache
        def dp(mask, curr):
            v = requests[curr][0]
            floor = requests[curr][1]

            if mask.bit_count() == 1:
                dist = abs(floor - start)
                return max(v, dist)

            nmask = mask ^ (1 << curr)

            res = inf
            for b in range(M):
                if b == curr:
                    continue
                if not (mask & (1 << b)):
                    continue

                # assume we came from that previous one
                
                prevTime = dp(nmask, b)
                prevFloor = requests[b][1]
                dist = abs(floor - prevFloor)
                time = max(prevTime + dist, v)
                res = min(res, time)

            return res

        ans = inf
        for b in range(M):
            v = requests[b][0]
            ans = min(ans, dp(fmask, b))

        dp.cache_clear()

        return ans
                
            
            