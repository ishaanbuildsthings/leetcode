# https://leetcode.com/problems/linked-list-in-binary-tree/description/
# difficulty: medium
# tags: linked list, tree, rolling hash

# Problem
# Given a binary tree root and a linked list with head as the first node.

# Return True if all the elements in the linked list starting from the head correspond to some downward path connected in the binary tree otherwise return False.

# In this context downward path means a path that starts at some node and goes downwards.


# Solution
# I did some recursive solution, and write rolling hash can get us linear.
# Looking back, I recursed on each node, and if we fully exhausted something we have a basecase. If we haven't yet started the matching process we recurse to a child, otherwise we start the process now.
# A rolling hash could involve serializing the linked list, descending down the tree maintaing a hash for our current descent, and matching it.

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

# can use rolling hash which can get us linear
class Solution:
    def isSubPath(self, head: Optional[ListNode], root: Optional[TreeNode]) -> bool:

        def recurse(linkedListHead, treeHead, isStarted):
            if not linkedListHead:
                return True

            if not treeHead:
                return False

            if isStarted:
                return (linkedListHead.val == treeHead.val
                and (recurse(linkedListHead.next, treeHead.left, True)
                or recurse(linkedListHead.next, treeHead.right, True)))

            # if we dont start
            option1 = recurse(head, treeHead.left, False) or recurse(head, treeHead.right, False)

            # if we start now
            option2 = linkedListHead.val == treeHead.val and (
                recurse(linkedListHead.next, treeHead.left, True) or recurse(linkedListHead.next, treeHead.right, True)
            )

            return option1 or option2


        return recurse(head, root, False)