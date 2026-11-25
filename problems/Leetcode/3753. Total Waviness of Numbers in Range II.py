class Solution:
    def totalWaviness(self, num1: int, num2: int) -> int:
        @cache
        def dp(i, pp, p, waves, strNum, isTight, started):
            if i == len(strNum):
                return waves
            resHere = 0
            up = 9 if not isTight else int(strNum[i])
            for d in range(up + 1):
                nt = isTight and d == up
                ns = started or d != 0
                npp = p
                np = d if d or started else None
                nwaves = waves
                if pp is not None and p is not None and started and p < pp and p < d:
                    nwaves += 1
                if pp is not None and p is not None and started and p > pp and p > d:
                    nwaves += 1
                resHere += dp(i + 1, npp, np, nwaves, strNum, nt, ns)
            return resHere
        
        return dp(0, None, None, 0, str(num2), True, False) - dp(0, None, None, 0, str(num1-1), True, False)
            
