class Solution:
    def correctBinaryTree(self, root: TreeNode) -> TreeNode:

        parents = defaultdict(list) # maps a node to potentially multiple parents
        depths = defaultdict(list)

        def dfs(node, par, depth):
            if not node:
                return
            parents[node].append(par)
            depths[node] = depth
            for child in [node.left, node.right]:
                if not child:
                    continue
                dfs(child, node, depth + 1)
        
        dfs(root, None, 0)

        nodeWithTwoParents = None
        for node, parentList in parents.items():
            if len(parentList) == 2:
                nodeWithTwoParents = node
                break
        
        p1, p2 = parents[nodeWithTwoParents]
        
        if depths[p1] > depths[p2]:
            defect = p1
        else:
            defect = p2
        
        def construct(node):
            if not node:
                return None
            if node == defect:
                return None
            left = construct(node.left)
            right = construct(node.right)
            node.left = left
            node.right = right
            return node
        
        return construct(root)