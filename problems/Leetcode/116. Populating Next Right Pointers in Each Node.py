"""
# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        
        # dfs version for better space complexity
        def dfs(node):
            if not node:
                return
            # if we have a next pointer, our right child connects to their left
            if node.next and node.right:
                node.right.next = node.next.left
            
            if node.left and node.right:
                node.left.next = node.right
            
            dfs(node.left)
            dfs(node.right)
        
        dfs(root)

        return root

