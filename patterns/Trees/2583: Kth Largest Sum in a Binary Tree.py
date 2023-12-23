# https://leetcode.com/problems/kth-largest-sum-in-a-binary-tree/
# difficulty: medium
# tags: bfs

# problem
# You are given the root of a binary tree and a positive integer k.

# The level sum in the tree is the sum of the values of the nodes that are on the same level.

# Return the kth largest level sum in the tree (not necessarily distinct). If there are fewer than k levels in the tree, return -1.

# Note that two nodes are on the same level if they have the same distance from the root.

# Solution, O(max(n, height log height)) time, O(n) space
# Get each level, sort, and return.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def kthLargestLevelSum(self, root: Optional[TreeNode], k: int) -> int:
        queue = collections.deque()
        queue.append(root)
        levelSums = []
        while len(queue):
            queueLength = len(queue)
            levelSum = 0
            for i in range(queueLength):
                node = queue.popleft() # pretend O(1) queue
                levelSum += node.val
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            levelSums.append(levelSum)
        if k > len(levelSums):
            return -1
        levelSums.sort(reverse=True)
        return levelSums[k-1]

