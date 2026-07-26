class Solution:
    def largestInteger(self, n: int, ss: int) -> int:
        res = -inf
        for v in range(100001):
            s = str(v)
            if len(s) > n:
                break
            tot = 0
            for d in s:
                tot += int(d)
            # print(tot)
            if tot == ss:
                res = v
        return res if res != -inf else -1