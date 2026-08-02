class Solution:
    def makeFancyString(self, s: str) -> str:
        resArr = []
        for c in s:
            if resArr and resArr[-1] == c and len(resArr) >= 2 and resArr[-2] == c:
                continue
            resArr.append(c)
        return ''.join(resArr)