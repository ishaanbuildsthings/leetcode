class Solution:
    def countNumbers(self, l: str, r: str, b: int) -> int:
        def toBase(s):
            out = []
            num = int(s)
            while num:
                lastDigit = num % b
                out.append(str(lastDigit))
                num -= lastDigit
                num //= b
            return ''.join(out)[::-1]
        
        lstr = toBase(l)
        rstr = toBase(r)
        diff = len(rstr) - len(lstr)
        lstr = ('0' * diff) + lstr

        MOD = 10**9 + 7

        @cache
        def dp(i, ltight, htight, prev):
            if i == len(rstr):
                return 1
            res = 0
            up = (b - 1) if not htight else int(rstr[i])
            down = 0 if not ltight else int(lstr[i])
            for d in range(down, up + 1):
                if d < prev:
                    continue
                nhtight = htight and d == up
                nltight = ltight and d == down
                ndp = dp(i + 1, nltight, nhtight, d)
                res += ndp
            return res % MOD
        
        return dp(0, True, True, -1)