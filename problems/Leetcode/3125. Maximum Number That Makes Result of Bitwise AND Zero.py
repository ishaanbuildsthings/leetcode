class Solution:
    def maxNumber(self, n: int) -> int:
        msb = n.bit_length() - 1
        return (1 << msb) - 1