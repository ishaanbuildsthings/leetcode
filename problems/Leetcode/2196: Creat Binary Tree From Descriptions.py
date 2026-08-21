# https://leetcode.com/problems/create-binary-tree-from-descriptions/description/
# difficulty: medium
# tags: binary tree

# Solution, O(n) time and space

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def createBinaryTree(self, descriptions: List[List[int]]) -> Optional[TreeNode]:
        valToNode = {}

        for parent, child, isLeft in descriptions:
            if parent not in valToNode:
                newParentNode = TreeNode(parent)
                valToNode[parent] = newParentNode
            parentNode = valToNode[parent]

            if child not in valToNode:
                newChildNode = TreeNode(child)
                valToNode[child] = newChildNode
            childNode = valToNode[child]

            if isLeft:
                parentNode.left = childNode
            else:
                parentNode.right = childNode

        # find the root
        allNodes = set(node for node in valToNode.values())
        for parent, child, isLeft in descriptions:
            allNodes.discard(valToNode[child])

        return list(allNodes)[0]

