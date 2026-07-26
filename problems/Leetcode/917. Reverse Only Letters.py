class Solution:
    def reverseOnlyLetters(self, s: str) -> str:
        resArr = [c for c in s]
        l = 0
        r = len(resArr) - 1
        while l < r:
            if resArr[l].isalpha() and resArr[r].isalpha():
                resArr[l], resArr[r] = resArr[r], resArr[l]
                l += 1
                r -= 1
            elif not resArr[l].isalpha():
                l += 1
            elif not resArr[r].isalpha():
                r -= 1
        return ''.join(resArr)