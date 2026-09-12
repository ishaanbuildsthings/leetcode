# https://leetcode.com/problems/largest-positive-integer-that-exists-with-its-negative/description/?envType=daily-question&envId=2024-05-02
# difficulty: easy

# Solution, n time n space

class Solution:
    def findMaxK(self, nums: List[int]) -> int:
        # n log n time + O(1) space
        # n^2 time + O(1) space
        # n time + O(n) time
        numSet = set(nums)
        res = None
        for num in numSet:
            if num * -1 in numSet:
                res = max(res, num) if res != None else num
        return res if res != None else -1
