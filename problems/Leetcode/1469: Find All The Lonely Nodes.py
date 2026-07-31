# https://leetcode.com/problems/find-all-the-lonely-nodes/description/?envType=weekly-question&envId=2024-04-15
# difficulty: easy
# tags: tree

# n time height space

class Solution:
    def getLonelyNodes(self, root: Optional[TreeNode]) -> List[int]:
        res = []
        def dfs(node):
            if not node:
                return
            if node.left and not node.right:
                res.append(node.left.val)
            if node.right and not node.left:
                res.append(node.right.val)
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return res