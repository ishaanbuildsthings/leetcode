# https://leetcode.com/problems/closest-subsequence-sum/
# difficulty: hard
# tags: meet in the middle, dfs

# Problem
# You are given an integer array nums and an integer goal.

# You want to choose a subsequence of nums such that the sum of its elements is the closest possible to goal. That is, if the sum of the subsequence's elements is sum, then you want to minimize the absolute difference abs(sum - goal).

# Return the minimum possible value of abs(sum - goal).

# Note that a subsequence of an array is an array formed by removing some elements (possibly all or none) of the original array.

# Solution
# We can do a branching factor of 2 and a depth of n/2 for two separate halves which is 2^(n/2). We can sort these then binary search to combine. Keep in mind dp(i, runningSum) is not n*2^n states, since you cannot have every runningSum for every i, so it's just recursion / dfs.

class Solution:
    def minAbsDifference(self, nums: List[int], goal: int) -> int:
        mid = len(nums) // 2
        left = nums[:mid + 1]
        right = nums[mid + 1:]

        leftSums = []
        rightSums = []

        def dfs(i, runningSum, arr, sums):
          if i == len(arr):
            sums.append(runningSum)
            return

          ifTake = dfs(i + 1, runningSum + arr[i], arr, sums)
          ifSkip = dfs(i + 1, runningSum, arr, sums)

        dfs(0, 0, left, leftSums)
        dfs(0, 0, right, rightSums)

        leftSums.sort()
        rightSums.sort()

        res = float('inf')

        for leftSum in leftSums:
          target = goal - leftSum
          idx = bisect.bisect_left(rightSums, target)
          if idx == len(rightSums):
            closest = rightSums[-1]
          elif idx == 0:
            closest = rightSums[0]
          else:
              if abs(target - rightSums[idx]) <= abs(target - rightSums[idx - 1]):
                  closest = rightSums[idx]
              else:
                  closest = rightSums[idx - 1]

          newSum = leftSum + closest
          res = min(res, abs(goal - newSum))

        return res


