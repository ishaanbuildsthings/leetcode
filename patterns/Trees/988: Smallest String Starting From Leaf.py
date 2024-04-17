# https://leetcode.com/problems/smallest-string-starting-from-leaf/description/?envType=daily-question&envId=2024-04-17
# difficulty: medium
# tags: tree

# Solution, bad n^2 solution, but I don't think n is doable anyway. This is height^2 space though but you could do height space

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
ABC = 'abcdefghijklmnopqrstuvwxyz'
numToCharMap = {
    i : ABC[i]
    for i in range(26)
}

class Solution:
    def smallestFromLeaf(self, root: Optional[TreeNode]) -> str:


        res = None

        def dfs(node, currStr):
            nonlocal res

            currStr += numToCharMap[node.val]

            if not node.left and not node.right:
                if res == None or currStr[::-1] < res:
                    res = currStr[::-1]
                return


            if node.left:
                dfs(node.left, currStr)
            if node.right:
                dfs(node.right, currStr)

        dfs(root, '')

        return res