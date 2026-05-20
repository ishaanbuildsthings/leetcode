class Solution:
    def nthMagicalNumber(self, n: int, a: int, b: int) -> int:

        def howManyMagicNumbersLTE(num):
            aMagics = num // a
            bMagics = num // b
            ABMagics = num // (lcm(a, b))
            magics = aMagics + bMagics - ABMagics
            return magics

        l = 1
        r = max(a, b) * n
        res = None
        while l <= r:
            m = (r + l) // 2
            magics = howManyMagicNumbersLTE(m)
            if magics < n:
                l = m + 1
            elif magics == n:
                res = m
                r = m - 1
            else:
                r = m - 1
        return res % (10**9 + 7)
        
