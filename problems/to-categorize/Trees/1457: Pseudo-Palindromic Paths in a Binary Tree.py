# https://leetcode.com/problems/pseudo-palindromic-paths-in-a-binary-tree/
# difficulty: medium
# tags: palindrome, binary tree

# Problem
# Given a binary tree where node values are digits from 1 to 9. A path in the binary tree is said to be pseudo-palindromic if at least one permutation of the node values in the path is a palindrome.

# Return the number of pseudo-palindromic paths going from the root node to leaf nodes.

# Solution, O(n) time and O(height) space, standard dfs, O(10) constant to track the count of each number type

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pseudoPalindromicPaths (self, root: Optional[TreeNode]) -> int:
        res = 0
        def dfs(node, accCounts):
            accCounts[node.val] += 1

            nonlocal res
            if not node.left and not node.right:
                oddsSeen = 0
                for key in accCounts:
                    amount = accCounts[key]
                    if amount % 2 == 1:
                        oddsSeen += 1
                    if oddsSeen > 1:
                        break
                if oddsSeen == 1 and sum(accCounts.values()) != 2:
                    res += 1
                elif oddsSeen == 0:
                    res += 1

            if node.left:
                dfs(node.left, accCounts)
            if node.right:
                dfs(node.right, accCounts)

            accCounts[node.val] -= 1


        dfs(root, defaultdict(int))

        return res
