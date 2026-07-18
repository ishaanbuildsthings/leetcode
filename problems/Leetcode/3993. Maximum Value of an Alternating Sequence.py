class Solution:
    def maximumValue(self, n: int, s: int, m: int) -> int:
        if n == 1:
            return s
        if m == 1:
            return 1 + s

        pairGain = m - 1 # up by m, down by 1

        # first is n
        # then go up one
        # then down up over and over
        if n % 2 == 0:
            upOne = s + m
            remainPairs = (n - 2) // 2
            return upOne + (pairGain * remainPairs)

        n -= 1
        upOne = s + m
        remainPairs = (n - 2) // 2
        return upOne + (pairGain * remainPairs)
            