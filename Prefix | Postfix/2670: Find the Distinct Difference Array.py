# https://leetcode.com/problems/find-the-distinct-difference-array/
# difficulty: easy
# tags: prefix, postifx

# Problem
# You are given a 0-indexed array nums of length n.

# The distinct difference array of nums is an array diff of length n such that diff[i] is equal to the number of distinct elements in the suffix nums[i + 1, ..., n - 1] subtracted from the number of distinct elements in the prefix nums[0, ..., i].

# Return the distinct difference array of nums.

# Note that nums[i, ..., j] denotes the subarray of nums starting at index i and ending at index j inclusive. Particularly, if i > j then nums[i, ..., j] denotes an empty subarray.

# Solution, O(n) time and space, just count the unique elements in prefix/postfix

class Solution:
    def distinctDifferenceArray(self, nums: List[int]) -> List[int]:
        left = defaultdict(int)
        right = defaultdict(int)
        for num in nums:
            right[num] += 1

        res = []
        for i in range(len(nums)):
            right[nums[i]] -= 1
            if right[nums[i]] == 0:
                del right[nums[i]]
            left[nums[i]] += 1
            res.append(len(left) - len(right))
        return res