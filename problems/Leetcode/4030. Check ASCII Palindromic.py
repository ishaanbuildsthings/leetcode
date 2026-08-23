class Solution:
    def isPalindromic(self, s: str) -> bool:
        def fn(c):
            num = ord(c)
            numS = bin(num)[2:]
            diff = 8 - len(numS)
            numS = ('0' * diff) + numS
            return numS

        res = []
        for v in s:
            # print(f'val is: {fn(v)}')
            res.append(fn(v))
        res = ''.join(res)
        return res == res[::-1]