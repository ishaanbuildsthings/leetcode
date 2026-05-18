MOD = 10**9 + 7
class Solution:
    def powerUpdate(self, nums: list[int], p: int, queries: list[list[int]]) -> list[int]:
        sl = SortedList(nums)

        @cache
        def modPow(b, e):
            if e == 0:
                return 1
            if e % 2:
                return (b * modPow(b, e - 1)) % MOD
            half = modPow(b, e // 2)
            return (half * half) % MOD
        
        res = []
        for v, k in queries:
            sl.add(v)
            x = sl[-k]
            p = modPow(p, x)
            res.append(p)
        
        return res
        