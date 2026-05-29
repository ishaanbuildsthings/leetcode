class Solution:
    def hasSameDigits(self, s: str) -> bool:
        # n = len(s)
        while len(s) > 2:
            newArr = []
            for i in range(len(s) - 1):
                newD = (int(s[i]) + int(s[i+1])) % 10
                newArr.append(str(newD))
            s = ''.join(newArr)
        return s[0] == s[1]