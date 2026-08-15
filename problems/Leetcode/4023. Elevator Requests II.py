class Solution:
    def elevatorRequests(self, n: int, start: int, requests: list[int]) -> int:
        requests.sort()

        fmin = lambda x, y : x if x < y else y
        
        # cache = [[[None, None] for _ in range(len(requests))] for _ in range(len(requests))]
        cache = [-1] * (len(requests) * len(requests) * 2)
        # @cache
        def dp(l, r, isLeft):
            if l == 0 and r == len(requests) - 1:
                return 0
            idx = (l * len(requests) + r) * 2 + isLeft
            if cache[idx] != -1:
                return cache[idx]

            width = r - l + 1
            outside = len(requests) - width
            res = inf
            # go down
            if l:
                if isLeft:
                    dist = requests[l]- requests[l - 1]
                else:
                    dist = requests[r] - requests[l - 1]
                answer = (outside * dist) + dp(l - 1, r, 1)
                res = answer
            # go up
            if r != len(requests) - 1:
                if isLeft:
                    dist = requests[r + 1] - requests[l]
                else:
                    dist = requests[r + 1] - requests[r]
                answer = (outside * dist) + dp(l, r + 1, 0)
                res = fmin(res, answer)
            cache[idx] = res
            return res
        
        res = inf
        for i, v in enumerate(requests):
            dist = abs(v - start)
            answer = dp(i, i, 1) + (dist * len(requests))
            res = fmin(res, answer)
        
        # dp.cache_clear()
        
        return res
                
