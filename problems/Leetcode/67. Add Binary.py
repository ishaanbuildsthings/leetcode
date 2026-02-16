class Solution:
    def addBinary(self, a: str, b: str) -> str:
        # scan bit by bit from right to left
        resArr = []
        big = max(len(a), len(b))
        carry = 0
        for i in range(big):
            d1 = int(a[len(a) - i - 1]) if len(a) - i - 1 >= 0 else 0
            d2 = int(b[len(b) - i - 1]) if len(b) - i - 1 >= 0 else 0
            tot = d1 + d2 + carry
            placed = tot % 2
            resArr.append(placed)
            if tot >= 2:
                carry = 1
            else:
                carry = 0
        if carry:
            resArr.append(carry)
            
        return ''.join(str(x) for x in resArr)[::-1]