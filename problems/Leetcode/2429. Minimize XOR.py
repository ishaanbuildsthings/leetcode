MAX_BITS = 30
class Solution:
    def minimizeXor(self, num1: int, num2: int) -> int:
        setBits = sum(
            1 if num2 & (1 << offset) != 0
            else 0
            for offset in range(MAX_BITS)
        )
        res = 0
        remaining = setBits
        for offset in range(MAX_BITS - 1, -1, -1):
            # skip unset bits
            if not (num1 & (1 << offset)):
                continue
            # if it is set, we nullify it if we can
            if remaining == 0:
                continue
            remaining -= 1
            res |= (1 << offset)

        if remaining == 0:
            return res

        # can do everything in one pass
        for offset in range(MAX_BITS):
            if res & (1 << offset):
                continue
            res |= (1 << offset)
            remaining -= 1
            if remaining == 0:
                return res
        

            