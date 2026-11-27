class Solution:
    def maxDiff(self, num: int) -> int:
        # can just use a greedy for logN instead of d^2 logN
        res = -inf
        big = -inf
        small = inf
        for orig in range(10):
            for dupe in range(10):
                if dupe == 0 and str(num)[0] == str(orig):
                    continue
                newNum = ''.join(c if c != str(orig) else str(dupe) for c in str(num))
                big = max(big, int(newNum))
                if int(newNum):
                    small = min(small, int(newNum))
                res = max(res, big - small)
        return res