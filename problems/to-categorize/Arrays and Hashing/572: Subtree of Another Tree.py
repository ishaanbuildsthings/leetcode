# TREE HASHING SOLUTION
# # Definition for a binary tree node.
# # class TreeNode:
# #     def __init__(self, val=0, left=None, right=None):
# #         self.val = val
# #         self.left = left
# #         self.right = right
# class Solution:
#     def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
#         MOD1 = 10**9 + 7
#         MOD2 = 2147483647

#         memo = set()

#         def hashAtNode(node, needToAdd):
#             if node is None:
#                 return (3, 7) # primes
            
#             left = hashAtNode(node.left, needToAdd)
#             right = hashAtNode(node.right, needToAdd)

#             left1 = (left[0] << 5) % MOD1
#             right1 = (right[0] << 1) % MOD1
#             left2 = (left[1] << 7) % MOD2
#             right2 = (right[1] << 1) % MOD2

#             hashPair = ((left1 + right1 + node.val) % MOD1, (left2 + right2 + node.val) % MOD2)

#             if needToAdd:
#                 memo.add(hashPair)
            
#             return hashPair
        
#         subHash = hashAtNode(subRoot, False)
#         hashAtNode(root, True)
#         if subHash in memo:
#             return True
#         return False




# LINEAR STRING HASH
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
# class Solution:
#     def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:

#         def preorder(node, lst):
#             if not node:
#                 lst.append('#')
#                 return
#             lst.append('X' + str(node.val) + 'X')
#             preorder(node.left, lst)
#             preorder(node.right, lst)
        
#         l1 = []
#         s1 = preorder(root, l1)
#         l2 = []
#         s2 = preorder(subRoot, l2)

#         s1 = ''.join(l1)
#         s2 = ''.join(l2)

#         # replace with rolling hash
#         return s2 in s1

        




# TREE HASHING
class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:

        MOD = 10**9 + 7
        BASE = 911
        def getHash(node, hashes):
            if not node:
                hashes.append(1)
                return 1
            h = node.val
            for child in [node.left, node.right]:
                chash = getHash(child, hashes)
                h *= BASE
                h += chash
                h %= MOD
            hashes.append(h)
            return h
        
        h2 = []
        subHashes = getHash(subRoot, h2)

        h1 = []
        hashes = getHash(root, h1)

        if h2[-1] in h1:
            return True
        
        return False
        
        

            