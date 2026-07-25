class Solution:
    def toHex(self, num: int) -> str:
        if num < 0:
            num += 2**32
        resArr = []
        if not num:
            return '0'
        while num:
            remain = num % 16
            if remain < 10:
                resArr.append(str(remain))
            else:
                index = remain - 10
                resArr.append(chr(index + ord('a')))
            num //= 16
        return ''.join(resArr)[::-1]