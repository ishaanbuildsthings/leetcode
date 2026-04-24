"""
# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List['Node']] = None):
        self.val = val
        self.children = children if children is not None else []
"""

class Solution:
    def moveSubTree(self, root: 'Node', p: 'Node', q: 'Node') -> 'Node':
        # p is a direct child of q already
        if p in q.children:
            return root
        
        originalRootIsP = root is p
        
        ppar = None
        qpar = None
        pInQ = False
        qInP = False
        def dfs(node, par, seenP, seenQ):
            nonlocal ppar, qpar, pInQ, qInP
            if node is p:
                ppar = par
                if seenQ:
                    pInQ = True
            if node is q:
                qpar = par
                if seenP:
                    qInP = True
            nseenP = seenP or node is p
            nseenQ = seenQ or node is q
            for child in node.children:
                dfs(child, node, nseenP, nseenQ)
        dfs(root, None, False, False)

        # if they are completely separate, sever
        if not pInQ and not qInP:
            # sever parent<>p
            if ppar:
                ppar.children.remove(p)
            q.children.append(p)
            return root if not originalRootIsP else q
        
        if pInQ:
            ppar.children.remove(p)
            q.children.append(p)
            return root if not originalRootIsP else q
        
        # q is in p
        # sever the parent<>q connection
        qpar.children.remove(q)
        q.children.append(p)
        # if we move P into Q when Q was in P the question asks us to basically swap them
        if ppar:
            i = ppar.children.index(p)
            ppar.children.remove(p)
            ppar.children.insert(i, q)


        return root if not originalRootIsP else q