class Solution:
    def isStrobogrammatic(self, num: str) -> bool:
        l = 0
        r = len(num) - 1
        inv = {
            '0' : '0',
            '1' : '1',
            '8' : '8',
            '6' : '9',
            '9' : '6'
        }

        while l <= r:
            if not num[l] in inv or not num[r] in inv:
                return False
            if num[l] != inv[num[r]]:
                return False
            l += 1
            r -= 1
        
        return True