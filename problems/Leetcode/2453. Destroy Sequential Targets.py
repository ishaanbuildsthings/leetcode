class Solution:
    def destroyTargets(self, nums: List[int], space: int) -> int:
        c = Counter()
        for v in nums:
            c[v % space] += 1
        big = max(c.values())
        res = inf
        for v in nums:
            modded = v % space
            if c[modded] == big:
                res = min(res, v)
        return res