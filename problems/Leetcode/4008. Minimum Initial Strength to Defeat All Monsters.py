class Solution:
    def minInitialStrength(self, monsters: list[int], boosts: list[list[int]]) -> int:
        n = len(monsters)
        sweep = [0] * (n + 1)
        for l, r, v in boosts:
            sweep[l] += v
            sweep[r + 1] -= v
        gain = [0] * n
        curr = 0
        for i, v in enumerate(sweep[:-1]):
            curr += v
            gain[i] = curr
        res = None
        l = 0
        r = 10**18
        while l <= r:
            m = (l + r) // 2
            currStr = m
            fail = False
            for i, v in enumerate(monsters):
                tempStr = currStr + gain[i]
                if tempStr < v:
                    fail = True
                    break
                currStr -= v
                currStr = max(currStr, 0)
            if fail:
                l = m + 1
            else:
                res = m
                r = m - 1
        return res
