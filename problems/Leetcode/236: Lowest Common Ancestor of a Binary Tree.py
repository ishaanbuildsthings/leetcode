# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        def dfs(node):
            if not node: return None
            if node in [p, q]: return node
            l, r = dfs(node.left), dfs(node.right)
            return node if l and r else l or r
        return dfs(root)

#         # we need to bubble to the bottom of our tree, then return up. we should carry information about if we have seen p or q. if at a node we have seen both p and q, we now just carry the LCA
#         def dfs(node):
#             # base case
#             if not node:
#                 return [False, False]

#             leftRes = dfs(node.left)
#             rightRes = dfs(node.right)

#             # if the leftRes is just the LCA, forward it
#             if isinstance(leftRes, TreeNode):
#                 return leftRes
#             # forward right
#             if isinstance(rightRes, TreeNode):
#                 return rightRes
#             seenP = leftRes[0] or rightRes[0] or node.val == p.val
#             seenQ = leftRes[1] or rightRes[1] or node.val == q.val
#             if seenP and seenQ:
#                 return node
#             else:
#                 return [seenP, seenQ]

#         return dfs(root)
            


# def depth(node, currDepth):
#     if not node:
#         return
#     nodeMap[node.val] = currDepth
#     depth(node.left, currDepth + 1)
#     depth(node.right, currDepth + 1)