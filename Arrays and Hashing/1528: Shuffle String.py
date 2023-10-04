# https://leetcode.com/problems/shuffle-string/
# difficulty: easy

# problem
# You are given a string s and an integer array indices of the same length. The string s will be shuffled such that the character at the ith position moves to indices[i] in the shuffled string.

# Return the shuffled string.

# Solution, O(n) time and space for the array, n space since the array and result may exist at the same time
class Solution:
    def restoreString(self, s: str, indices: List[int]) -> str:
        resArr = [None for _ in range(len(s))]
        for i in range(len(s)):
            resArr[indices[i]] = s[i]
        return ''.join(resArr)