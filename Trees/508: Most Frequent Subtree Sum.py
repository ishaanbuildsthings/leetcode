# https://leetcode.com/problems/most-frequent-subtree-sum/description/
# difficulty: medium
# tags: binary tree

# Problem
# Given the root of a binary tree, return the most frequent subtree sum. If there is a tie, return all the values with the highest frequency in any order.

# The subtree sum of a node is defined as the sum of all the node values formed by the subtree rooted at that node (including the node itself).

# Solution, dfs and count all of them, then get the max, O(n) time and space

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findFrequentTreeSum(self, root: Optional[TreeNode]) -> List[int]:
        counts = defaultdict(int)

        def dfs(node):
            if not node:
                return 0
            leftSum = dfs(node.left)
            rightSum = dfs(node.right)
            totalSum = node.val + leftSum + rightSum
            counts[totalSum] += 1
            return totalSum

        dfs(root)

        countsToNum = defaultdict(list)
        for sumType in counts:
            amountOfOccurencesOfSumType = counts[sumType]
            countsToNum[amountOfOccurencesOfSumType].append(sumType)

        maxCount = max(countsToNum.keys())
        return countsToNum[maxCount]