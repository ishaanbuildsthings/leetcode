# https://leetcode.com/problems/find-leaves-of-binary-tree/description/
# difficulty: medium
# tags: binary tree

# Problem
# Given the root of a binary tree, collect a tree's nodes as if you were doing this:

# Collect all the leaf nodes.
# Remove all the leaf nodes.
# Repeat until the tree is empty.

# Solution, O(max depth * n) time, O(max depth) space
# Each iteration, iterate to the bottom, get the leaves, parse them out, add to result, and repeat. I believe a faster solution may exist where we create parent points and start at the bottom, moving up and determining what is a leaf. I can also see something about assigning nodes to different buckets as we ascend  based on how far that node is from being a leaf, which might be O(n) time and space, or even a recursive solution that is O(n) time and O(height) space
# Solution 2, I think we could have parent pointers and make it fast, use a seen set and just move up

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findLeaves(self, root: Optional[TreeNode]) -> List[List[int]]:
        res = []
        def gatherAndRemoveLeaves(node, bucket):
            # if left is a leaf
            if node.left and not node.left.left and not node.left.right:
                bucket.append(node.left.val)
                node.left = None
            if node.right and not node.right.left and not node.right.right:
                bucket.append(node.right.val)
                node.right = None

            if node.left:
                gatherAndRemoveLeaves(node.left, bucket)
            if node.right:
                gatherAndRemoveLeaves(node.right, bucket)

        dummy = TreeNode(val=None, left=root, right=None)
        res = []
        while dummy.left:
            bucket = []
            gatherAndRemoveLeaves(dummy, bucket)
            res.append(bucket)
        return res