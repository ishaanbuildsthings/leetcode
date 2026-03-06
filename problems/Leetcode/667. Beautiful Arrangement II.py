class Solution:
    def constructArray(self, n: int, k: int) -> List[int]:
        res = []

        if k == 1:
            return list(range(1, n + 1))

        # 1-10-2-9-3-...
        gaps = set()
        vals = list(range(1, n + 1))
        res = []
        l = 0
        r = len(vals) - 1
        while l <= r:
            if len(gaps) == k - 1:
                break
            res.append(vals[l])
            l += 1
            if len(res) > 1:
                gap = abs(res[-1] - res[-2])
                gaps.add(gap)
            if len(gaps) == k - 1:
                break
            if l <= r:
                res.append(vals[r])
                gaps.add(abs(res[-1] - res[-2]))
                r -= 1
        
        lo = vals[l]
        hi = vals[r]
        if abs(lo - res[-1]) == 1:
            for num in range(lo, hi + 1):
                res.append(num)
        else:
            for num in range(hi, lo - 1, -1):
                res.append(num)

        return res
            




