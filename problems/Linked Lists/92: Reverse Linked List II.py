# https://leetcode.com/problems/reverse-linked-list-ii/?envType=daily-question&envId=2023-09-07
# Difficulty: Medium
# Tags: Linked Lists

# Problem
# Given the head of a singly linked list and two integers left and right where left <= right, reverse the nodes of the list from position left to position right, and return the reversed list.

# Solution, O(n) time, O(1) space
# Find the previous node, reverse the next portion, rewire the previous in and the end of the portion into the node after.

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        # find the node before left
        prev = None
        pointer = head
        for i in range(left):
            prev = pointer
            pointer = pointer.next

        def reverse_list_and_get_next(linked_list, reverse_size):
            new_tail = linked_list
            pointer = linked_list
            prev = None
            for i in range(reverse_size):
                next_node = pointer.next
                pointer.next = prev
                prev = pointer
                pointer = next_node
            new_tail.next = pointer
            return prev

        rev_list_head = reverse_list_and_get_next(pointer, right - left + 1)
        if prev:
            prev.next = rev_list_head
            return head
        return rev_list_head


