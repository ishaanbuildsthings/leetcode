# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def deleteNode(self, node):
        """
        :type node: ListNode
        :rtype: void Do not return anything, modify node in-place instead.
        """

        curr = node

        if not curr.next.next:
            curr.val = curr.next.val
            curr.next = None

        while curr and curr.next:
            curr.val = curr.next.val
            if not curr.next.next:
                curr.next = None
            curr = curr.next
        