ABC = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def canConvertString(self, s: str, t: str, k: int) -> bool:
        if len(s) != len(t):
            return False

        def calcshift(a, b):
            bIndex = ABC.index(b)
            aIndex = ABC.index(a)
            if bIndex >= aIndex:
                return bIndex - aIndex
            return 26 - (aIndex - bIndex)
        
        c = Counter()
        for i in range(len(s)):
            c[calcshift(s[i],t[i])] += 1
        del c[0]

        for shiftAmt in c:
            times = c[shiftAmt]
            bigK = ((times - 1) * 26) + shiftAmt
            if bigK > k:
                return False
        return True
