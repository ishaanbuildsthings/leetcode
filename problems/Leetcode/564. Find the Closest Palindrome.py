class Solution:
    def nearestPalindromic(self, s: str) -> str:
        n = len(s)
        half = ceil(n / 2)

        def build(left):
            if n % 2 == 0:
                return left + left[::-1]
            mini = left[:-1]
            return mini + left[-1] + mini[::-1]

        base = int(s[:half])
        options = []
        for delta in (-1, 0, 1):
            options.append(build(str(base + delta)))
        options.append(str(10**n + 1))
        options.append(str(10**(n-1) - 1))

        dist = inf
        res = inf
        for v in options:
            if v == s:
                continue
            v = int(v)
            diff = abs(int(v) - int(s))
            if diff < dist:
                dist = diff
                res = v
            elif diff == dist:
                res = min(res, v)
        
        return str(res)




