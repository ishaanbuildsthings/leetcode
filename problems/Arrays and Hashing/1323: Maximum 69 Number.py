# https://leetcode.com/problems/maximum-69-number/description/
# difficulty: easy

# Solution, O(log n) time and space, can use math instead of strings

class Solution:
    def maximum69Number (self, num: int) -> int:
        strNum = str(num)
        for i in range(len(strNum)):
            if strNum[i] == '6':
                return int(strNum[:i] + '9' + strNum[i+1:])
        return num