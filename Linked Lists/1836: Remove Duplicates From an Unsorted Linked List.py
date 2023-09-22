# https://leetcode.com/problems/remove-duplicates-from-an-unsorted-linked-list/
# Difficulty: Medium
# Tags: Linked List

# Problem
# Given the head of a linked list, find all the values that appear more than once in the list and delete the nodes that have any of those values.

# Return the linked list after the deletions.

# Solution, O(n) space and time
# Get the counts. Then iterate again and remove as needed. We use a dummy to simplify removing from the beginning.

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicatesUnsorted(self, head: ListNode) -> ListNode:
        counts = defaultdict(int)
        pointer = head
        while pointer:
            counts[pointer.val] += 1
            pointer = pointer.next

        dummy = ListNode()
        dummy.next = head
        pointer = dummy
        while pointer and pointer.next:
            if counts[pointer.next.val] > 1:
                pointer.next = pointer.next.next
            else:
                pointer = pointer.next
        return dummy.next