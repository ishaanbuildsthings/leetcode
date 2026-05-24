class Solution:
    def smallestNumber(self, n: int) -> str:
        if n == 1:
            return '1'

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
            return '-1'
        
        resArr = []
        for digit in range(2, 10):
            resArr.extend([str(digit)] * c[digit])
        return ''.join(resArr)