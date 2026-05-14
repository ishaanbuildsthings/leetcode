# https://leetcode.com/problems/delete-the-middle-node-of-a-linked-list/description/
# Difficulty: medium
# tags: linked list

# Problem
# You are given the head of a linked list. Delete the middle node, and return the head of the modified linked list.

# The middle node of a linked list of size n is the ⌊n / 2⌋th node from the start using 0-based indexing, where ⌊x⌋ denotes the largest integer less than or equal to x.

# For n = 1, 2, 3, 4, and 5, the middle nodes are 0, 1, 1, 2, and 2, respectively.

# Solution, O(n) time O(1) space, slow and faster pointers. Could also initialize fast to start later so we don't need a prev pointer.

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteMiddle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = head
        fast = head
        prevSlow = None
        while fast and fast.next:
            prevSlow = slow
            slow = slow.next
            fast = fast.next.next
        # edge case
        if not prevSlow:
            return None
        prevSlow.next = prevSlow.next.next
        return head