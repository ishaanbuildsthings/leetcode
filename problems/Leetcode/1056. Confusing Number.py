class Solution:
    def confusingNumber(self, n: int) -> bool:
        if any(char in '23457' for char in str(n)):
            return False
        
        flip = {
            '6' : '9',
            '9' : '6',
            '0' : '0',
            '1' : '1',
            '8' : '8'
        }

        l = 0
        r = len(str(n)) - 1
        while l <= r:
            leftC = str(n)[l]
            rightC = str(n)[r]
            if flip[leftC] != rightC:
                return True
            l += 1
            r -= 1
        
        return False
                