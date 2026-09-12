# https://leetcode.com/problems/convert-an-array-into-a-2d-array-with-conditions/
# difficulty: medium

# problem
# You are given an integer array nums. You need to create a 2D array from nums satisfying the following conditions:

# The 2D array should contain only the elements of the array nums.
# Each row in the 2D array contains distinct integers.
# The number of rows in the 2D array should be minimal.
# Return the resulting array. If there are multiple answers, return any of them.

# Note that the 2D array can have a different number of elements on each row.

# Solution, O(n) time and space
# Count the number of occurences of everything, add elements as needed. Could do it in fewer passes and just check if the array in our result already exists yet.

class Solution:
    def findMatrix(self, nums: List[int]) -> List[List[int]]:
        counts = collections.Counter(nums)
        res = []
        maxCount = max(counts.values())
        for i in range(maxCount):
            res.append([])

        for numType in counts:
            amount = counts[numType]
            for i in range(amount):
                res[i].append(numType)

        return res