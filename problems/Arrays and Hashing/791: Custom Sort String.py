# https://leetcode.com/problems/custom-sort-string/
# difficulty: medium


# Solution
class Solution:
    def customSortString(self, order: str, s: str) -> str:
        frqs = Counter(s)
        resArr = []
        for char in order:
            for occurence in range(frqs[char]):
                resArr.append(char)
                frqs[char] -= 1
        for char in frqs:
            for occurence in range(frqs[char]):
                resArr.append(char)
        return ''.join(resArr)