class Solution:
    def balancedString(self, s: str) -> int:
        n = len(s)

        def do(x):
            c = Counter(s)
            for i in range(x):
                c[s[i]] -= 1
            if max(c.values()) <= n / 4:
                return True
            for r in range(x, n):
                c[s[r]] -= 1
                c[s[r - x]] += 1
                if max(c.values()) <= n / 4:
                    return True
            return False

        l = 0
        r = n
        res = None
        while l <= r:
            m = (r + l) // 2
            if do(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        return res