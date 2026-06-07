class Solution:
    def findComplement(self, num: int) -> int:
        msb = num.bit_length()
        fmask = (1 << msb) - 1
        return fmask ^ num