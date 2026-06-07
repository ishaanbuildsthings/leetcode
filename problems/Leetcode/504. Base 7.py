class Solution:
    def convertToBase7(self, num: int) -> str:
        resStr = ''
        neg = num < 0
        num = abs(num)
        if not num:
            return '0'
        while num:
            remain = num % 7
            resStr = str(remain) + resStr
            num //= 7
        return '-' + resStr if neg else resStr