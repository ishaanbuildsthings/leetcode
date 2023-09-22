# https://leetcode.com/problems/number-of-subarrays-having-even-product/description/
# difficulty: Medium
# tags: kadane's

# Problem
# Given a 0-indexed integer array nums, return the number of subarrays of nums having an even product.

# Solution, O(n) time O(1) space
# Even subarrays total-odds. Odds are ones with no even. Use kadane's to find that.


class Solution:
  def evenProduct(self, nums: List[int]) -> int:
      n = len(nums)
      totalSubarrays = n * (n + 1) / 2
      # find amount of odd subarrays

      oddSubarrays = 0
      streak = 0 # maintain a kadane's streak for how many odd numbers we have seen in a row
      for i in range(len(nums)):
          if nums[i] % 2 == 1:
              streak += 1
          else:
              streak = 0
          oddSubarrays += streak
      return int(totalSubarrays - oddSubarrays)


