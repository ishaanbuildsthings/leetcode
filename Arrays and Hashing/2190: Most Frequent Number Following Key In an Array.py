# https://leetcode.com/problems/most-frequent-number-following-key-in-an-array/description/
# difficulty: easy
# tags: functional

# Problem
# You are given a 0-indexed integer array nums. You are also given an integer key, which is present in nums.

# For every unique integer target in nums, count the number of times target immediately follows an occurrence of key in nums. In other words, count the number of indices i such that:

# 0 <= i <= nums.length - 2,
# nums[i] == key and,
# nums[i + 1] == target.
# Return the target with the maximum count. The test cases will be generated such that the target with maximum count is unique.

# Solution
# O(n) time and space, nice walrus operator!

class Solution:
    def mostFrequent(self, nums: List[int], key: int) -> int:
        return max(
            frqs := Counter(
                nums[i]
                for i in range(1, len(nums))
                if nums[i - 1] == key
            ),
            key=frqs.get
        )