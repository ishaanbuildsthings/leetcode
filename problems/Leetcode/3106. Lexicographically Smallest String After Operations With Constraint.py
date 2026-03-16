class Solution:
    def getSmallestString(self, s: str, k: int) -> str:
        res = []
        opsLeft = k
        for c in s:
            distToA = min(ord(c) - ord('a'), 26 - (ord(c) - ord('a')))
            if opsLeft >= distToA:
                res.append('a')
                opsLeft -= distToA
            else:
                res.append(chr(ord(c) - opsLeft))
                opsLeft = 0
        return ''.join(res)