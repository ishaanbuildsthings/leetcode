# https://leetcode.com/problems/maximum-binary-tree/description/
# Difficulty: Medium
# Tags: binary tree

# Problem
# You are given an integer array nums with no duplicates. A maximum binary tree can be built recursively from nums using the following algorithm:

# Create a root node whose value is the maximum value in nums.
# Recursively build the left subtree on the subarray prefix to the left of the maximum value.
# Recursively build the right subtree on the subarray suffix to the right of the maximum value.
# Return the maximum binary tree built from nums.

# Solution, O(n^2) time and O(n^2) space
# Find the max and recurse on the left and right. At first I thought we needed to precompute all possible maxes but I realized there's only n states (despite being defined by l and r) so we can find the max inside the build function, which would also save on space complexity.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def constructMaximumBinaryTree(self, nums: List[int]) -> Optional[TreeNode]:
        cache = [[None for _ in range(len(nums))] for _ in range(len(nums))] # cache[l][r] tells us the index of the max number in [l:r]
        for l in range(len(nums)):
            maxIndex = l
            maxNum = nums[l]
            for r in range(l, len(nums)):
                if nums[r] > maxNum:
                    maxIndex = r
                    maxNum = nums[r]
                cache[l][r] = maxIndex

        def build(l, r):
            # base case
            if l == r:
                return TreeNode(nums[l])
            # edge case
            if l > r:
                return None

            maxIndex = cache[l][r]
            root = TreeNode(nums[maxIndex])
            root.left = build(l, maxIndex - 1)
            root.right = build(maxIndex + 1, r)
            return root

        return build(0, len(nums) - 1)