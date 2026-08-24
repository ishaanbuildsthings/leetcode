class Solution:
    def smallestFactorization(self, n: int) -> int:
        # basically copied code from https://leetcode.com/problems/smallest-number-with-given-digit-product/description/
        
        if n == 1:
            return 1

        c = Counter()
        nextDivide = 9
        curr = n
        while nextDivide > 1:
            if curr % nextDivide == 0:
                c[nextDivide] += 1
                curr //= nextDivide
            else:
                nextDivide -= 1
        if curr != 1:
            return 0
        
        resArr = []
        for digit in range(2, 10):
            resArr.extend([str(digit)] * c[digit])
        res = int(''.join(resArr))
        if res > 2**31:
            return 0
        return res

        