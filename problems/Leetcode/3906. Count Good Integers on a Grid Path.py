class Solution:
    def countGoodIntegersOnPath(self, l: int, r: int, directions: str) -> int:
        rstr = '0' * (16 - len(str(r))) + str(r)
        lstr = '0' * (16 - len(str(l))) + str(l)
        eyes = [0]
        r = c = 0
        for d in directions:
            r += d == 'D'
            c += d == 'R'
            eyes.append(4 * r + c)
        @cache
        def dp(i, ltight, htight, prevDigit, eyeI):
            if i == len(rstr):
                return 1
            low = 0 if not ltight else int(lstr[i])
            hi = 9 if not htight else int(rstr[i])
            res = 0
            isOcc = eyeI < len(eyes) and i == eyes[eyeI]
            for d in range(low, hi + 1):
                nhtight = htight and d == hi
                nltight = ltight and d == low
                if isOcc and d < prevDigit:
                    continue
                nprev = prevDigit if not isOcc else d
                neyeI = eyeI if not isOcc else eyeI + 1
                res += dp(i + 1, nltight, nhtight, nprev, neyeI)
            return res
        return dp(0, True, True, -1, 0)