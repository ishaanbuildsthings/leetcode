# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Codec:

    def serialize(self, root: Optional[TreeNode]) -> str:
        """Encodes a tree to a single string.
        """
        if not root:
            return 'none'
        par = {} # maps node value to parent value
        par[root.val] = -1 # sentinel
        def dfs(node, parent):
            if not node:
                return
            if node != root:
                par[node.val] = parent.val
            dfs(node.left, node)
            dfs(node.right, node)
        dfs(root, None)
        return json.dumps(par)


        

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """Decodes your encoded data to tree.
        """
        if data == 'none':
            return None
        data = json.loads(data)
        vToNode = {}
        for nodeVal, parentVal in data.items():
            if int(parentVal) == -1:
                rootVal = nodeVal
        
        for nodeVal, parentVal in data.items():
            nodeVal = int(nodeVal)
            parentVal = int(parentVal)
            if nodeVal not in vToNode:
                vToNode[nodeVal] = TreeNode(nodeVal)
            if parentVal == -1:
                continue
            if parentVal not in vToNode:
                vToNode[parentVal] = TreeNode(parentVal)
            if nodeVal < parentVal:
                vToNode[parentVal].left = vToNode[nodeVal]
            else:
                vToNode[parentVal].right = vToNode[nodeVal]

        return vToNode[int(rootVal)]
                

# Your Codec object will be instantiated and called as such:
# Your Codec object will be instantiated and called as such:
# ser = Codec()
# deser = Codec()
# tree = ser.serialize(root)
# ans = deser.deserialize(tree)
# return ans