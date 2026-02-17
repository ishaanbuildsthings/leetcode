class Solution:
    def myPow(self, x: float, n: int) -> float:
        inv = n < 0
        n = abs(n)
        res = 1
        base = x

        # 5^13 = 5^8 * 5^4 * 5^1

        for i in range(32):
            if (n >> i) & 1:
                res *= base
            base *= base
        
        return res if not inv else 1 / res

        # while loop version
        # while n:
        #     if n % 2:
        #         res *= base
        #     base *= base
        #     n //= 2
        # if inv:
        #     return 1 / res
        # return res
            