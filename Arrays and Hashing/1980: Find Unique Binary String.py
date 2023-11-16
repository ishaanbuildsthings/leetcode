# https://leetcode.com/problems/find-unique-binary-string/description/?envType=daily-question&envId=2023-11-16
# difficulty: medium

# Problem
# Given an array of strings nums containing n unique binary strings each of length n, return a binary string of length n that does not appear in nums. If there are multiple answers, you may return any of them.

# Solution, O(n) time and space (we cannot make assumptions about the array). Great question. You can solve it with a trie, generating n+1 random numbers, or diagonalization.

class Solution:
    def findDifferentBinaryString(self, nums: List[str]) -> str:
        resArr = []
        for i in range(len(nums)):
            binaryString = nums[i]
            bitStr = binaryString[i]
            resArr.append('0' if bitStr == '1' else '1')
        return ''.join(resArr)