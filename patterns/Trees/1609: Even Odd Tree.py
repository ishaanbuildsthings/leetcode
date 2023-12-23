# https://leetcode.com/problems/even-odd-tree/description/
# difficulty: medium
# tags: tree, bfs

# Problem
# A binary tree is named Even-Odd if it meets the following conditions:

# The root of the binary tree is at level index 0, its children are at level index 1, their children are at level index 2, etc.
# For every even-indexed level, all nodes at the level have odd integer values in strictly increasing order (from left to right).
# For every odd-indexed level, all nodes at the level have even integer values in strictly decreasing order (from left to right).
# Given the root of a binary tree, return true if the binary tree is Even-Odd, otherwise return false.

# Solution, go row by row and validate. O(n) time and space. I did it in one pass, but it isn't necessarily better in machine instructions due to multiple if checks.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isEvenOddTree(self, root: Optional[TreeNode]) -> bool:
        # edge case
        if root.val % 2 == 0:
            return False

        q = collections.deque()
        q.append(root)
        level = 0
        while q:
            length = len(q)
            prevNode = q.popleft()
            prev = prevNode.val
            # edge case, could be handled differently too but then you have to change how you make prev
            if prev % 2 == level % 2:
                return False
            if prevNode.left:
                q.append(prevNode.left)
            if prevNode.right:
                q.append(prevNode.right)
            for i in range(length - 1):
                popped = q.popleft()
                if level % 2 == 0 and popped.val % 2 == 0:
                    return False
                if level % 2 == 1 and popped.val % 2 == 1:
                    return False
                if level % 2 == 0 and popped.val <= prev:
                    return False
                if level % 2 == 1 and popped.val >= prev:
                    return False
                prev = popped.val
                if popped.left:
                    q.append(popped.left)
                if popped.right:
                    q.append(popped.right)
            level += 1
        return True
