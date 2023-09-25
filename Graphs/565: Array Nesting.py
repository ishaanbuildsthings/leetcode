# https://leetcode.com/problems/array-nesting/description/
# difficulty: medium
# tags: dfs, graph, disonnected

# problem
# You are given an integer array nums of length n where nums is a permutation of the numbers in the range [0, n - 1].

# You should build a set s[k] = {nums[k], nums[nums[k]], nums[nums[nums[k]]], ... } subjected to the following rule:

# The first element in s[k] starts with the selection of the element nums[k] of index = k.
# The next element in s[k] should be nums[nums[k]], and then nums[nums[nums[k]]], and so on.
# We stop adding right before a duplicate element occurs in s[k].
# Return the longest length of a set s[k].

# Solution, O(n) time and space
# Like blindfold rubik's cube cycles, we just have a set of graph cycles. DFS in one, mark all as seen, and continue.

class Solution:
    def arrayNesting(self, nums: List[int]) -> int:
        seen = set() # holds indices of numbers we have seen

        # gets us the size of the chain starting from index
        def dfs(index):
            seen.add(index)
            num = nums[index]
            if num in seen:
                return 0
            return 1 + dfs(num)


        res = 0
        for i in range(len(nums)):
            num = nums[i]
            if not num in seen:
                res = max(res, dfs(i))
        return res + 1 # size of set not length of chain


