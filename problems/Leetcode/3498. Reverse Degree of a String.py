class Solution:
    def reverseDegree(self, s: str) -> int:
        def getRev(character):
            myPos = ord(character) - ord('a')
            return 26 - myPos
        res = 0
        for i in range(len(s)):
            res += (i + 1) * getRev(s[i])
        return res