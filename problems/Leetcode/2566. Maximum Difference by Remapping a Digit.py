class Solution:
    def minMaxDifference(self, num: int) -> int:
        num = str(num)
        # can use greedy
        big = -inf
        small = inf
        for orig in range(10):
            for replace in range(10):
                newStr = ''.join([x if x != str(orig) else str(replace) for x in num])
                big = max(big, int(newStr))
                small = min(small, int(newStr))
        return big - small