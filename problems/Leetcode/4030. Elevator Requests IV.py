class Solution:
    def elevatorRequests(self, n: int, start: int, requests: list[list[int]]) -> int:
        requests.sort(key=lambda x : x[1])
        @cache
        def dp(l, r, isLeft):
            t, pos = requests[l if isLeft else r]
            if l == 0 and r is None:
                return max(t, abs(pos - start))
            if r == len(requests) - 1 and l is None:
                return max(t, abs(pos - start))
            res = inf
            
            if isLeft:
                if l is not None and l != 0:
                    prevT, prevPos = requests[l - 1]
                    fromL = max(dp(l - 1, r, True) + abs(prevPos - pos), t)
                    res = min(res, fromL)
                if r is not None:
                    prevT, prevPos = requests[r]
                    fromR = max(dp(l - 1 if l else None, r, False) + abs(prevPos - pos), t)
                    res = min(res, fromR)
            else:
                if l is not None:
                    prevT, prevPos = requests[l]
                    fromL = max(dp(l, r + 1 if r + 1 < len(requests) else None, True) + abs(prevPos - pos), t)
                    res = min(res, fromL)
                if r is not None and r != len(requests) - 1:
                    prevT, prevPos = requests[r + 1]
                    fromR = max(dp(l, r + 1, False) + abs(prevPos - pos), t)
                    res = min(res, fromR)
            
            return res
        
        res = inf
        for i in range(len(requests) - 1):
            res = min(res, dp(i, i + 1, True))
            res = min(res, dp(i, i + 1, False))
        res = min(res, dp(None, 0, False))
        res = min(res, dp(len(requests) - 1, None, True))

        dp.cache_clear()
        return res

            
