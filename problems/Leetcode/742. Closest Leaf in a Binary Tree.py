# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findClosestLeaf(self, root: Optional[TreeNode], k: int) -> int:
        g = defaultdict(list) # node -> adj nodes
        kNode = None
        def makeG(node):
            nonlocal kNode
            if node.val == k:
                kNode = node
            if node.left:
                g[node].append(node.left)
                g[node.left].append(node)
                makeG(node.left)
            if node.right:
                g[node].append(node.right)
                g[node.right].append(node)
                makeG(node.right)
        makeG(root)
        seen = set()
        seen.add(kNode)
        q = deque()
        q.append(kNode)
        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                if not popped.left and not popped.right:
                    return popped.val
                for adj in g[popped]:
                    if not adj in seen:
                        seen.add(adj)
                        q.append(adj)
        
            
