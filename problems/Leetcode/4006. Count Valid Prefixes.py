class Solution:
    def countValidPrefixes(self, s: str) -> int:
        ones = res = 0
        for i, v in enumerate(s):
            ones += v == '1'
            zeroes = (i + 1) - ones
            res += (ones - 1 == zeroes) or (zeroes - 1 == ones) or (zeroes == ones)
        return res
