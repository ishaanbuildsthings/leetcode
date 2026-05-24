class Solution:
    def bitwiseComplement(self, n: int) -> int:
        if not n: return 1
        l = n.bit_length()
        fmask = (1 << l) - 1
        inv = fmask ^ n
        return inv