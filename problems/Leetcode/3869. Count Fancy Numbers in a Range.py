class Solution:
    def countFancy(self, l: int, r: int) -> int:

        @cache
        def good(num):
            s = str(num)
            if all(int(s[i]) < int(s[i+1]) for i in range(len(s) - 1)):
                return True
            if all(int(s[i]) > int(s[i+1]) for i in range(len(s) - 1)):
                return True
            return False

        @cache
        def dp(strNum, i, tight, tot, prevD, up, down, zero):
            if i == len(strNum):
                return 1 if (good(tot) or up or down) else 0
            upper = 9 if not tight else int(strNum[i])
            resHere = 0
            for d in range(upper + 1):
                ntight = tight and d == upper
                ntot = tot + d
                nzero = zero and d == 0
                nup = (up and d > prevD) or (i == 0) or (zero)
                ndown = (down and d < prevD) or (i == 0) or (zero)
                resHere += dp(strNum, i + 1, ntight, ntot, d, nup, ndown, nzero)
            return resHere

        hi = dp(str(r), 0, True, 0, -1, True, True, True)
        loS = str(l - 1)
        while len(loS) < len(str(r)):
            loS = '0' + loS
        # print(loS)
        lo = dp(loS, 0, True, 0, -1, True, True, True)
        dp.cache_clear()
        return hi - lo
                
            