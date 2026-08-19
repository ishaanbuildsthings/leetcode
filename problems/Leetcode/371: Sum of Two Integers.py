class Solution:
    def getSum(self, a: int, b: int) -> int:
        res = 0
        carry = 0
        for i in range(12):
            abit = (a >> i) & 1
            bbit = (b >> i) & 1
            remain = abit ^ bbit ^ carry
            if carry:
                carry = abit | bbit
            else:
                carry = abit & bbit
            if remain:
                res |= (1 << i)
        if res & (1 << 11):
            res = ~(res ^ 0xFFF)
        # if res & (1 << 11):
        #     res -= 1 << 12 # bigger because we need to undo the previous positive AND subtract a bigger negative, like go from +2048 to -4192
        return res