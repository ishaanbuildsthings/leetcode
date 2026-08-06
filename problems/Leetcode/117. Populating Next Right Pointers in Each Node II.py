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
    def connect(self, root: 'Node') -> 'Node':

        # dfs version for better space complexity
        def dfs(node):
            if not node:
                return

            if not node.left and not node.right:
                return

            # find the first node on the right with a child

            if node.right:
                toConnect = node.right
            elif node.left:
                toConnect = node.left
            
            currNext = node.next
            while currNext:
                if not currNext.left and not currNext.right:
                    currNext = currNext.next
                    continue
                if currNext.left:
                    toConnect.next = currNext.left
                    break
                if currNext.right:
                    toConnect.next = currNext.right
                    break

            if node.left and node.right:
                node.left.next = node.right
            
            dfs(node.right) # tricky part, need to do the right side first
            dfs(node.left)
            

        dfs(root)

        return root