# https://leetcode.com/problems/split-linked-list-in-parts/description/?envType=daily-question&envId=2023-09-06
# Difficulty: Medium
# Tags: Linked Lists

# Problem
# Given the head of a singly linked list and an integer k, split the linked list into k consecutive linked list parts.

# The length of each part should be as equal as possible: no two parts should have a size differing by more than one. This may lead to some parts being null.

# The parts should be in the order of occurrence in the input list, and parts occurring earlier should always have a size greater than or equal to parts occurring later.

# Return an array of the k parts.

# Solution O(n + k) time, O(1) space
# The main problem comes down to figuring out the size for every part. The first n%k parts have size n/k + 1 and the rest have size n/k or something like that. I deduced it another way.

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def splitListToParts(self, head: Optional[ListNode], k: int) -> List[Optional[ListNode]]:
        size = 0
        pointer = head
        while pointer:
            size += 1
            pointer = pointer.next
        bigger_size = math.ceil(size / k)
        smaller_size = bigger_size - 1

        # returns a linked list of size n by severing the ending connection, also returns the head of the linked list afterwards, always assumes we have n nodes left
        def get_slice(linked_list, n):
            if not linked_list:
                return [None, None]
            slice_head = linked_list
            pointer = linked_list
            for i in range(n - 1):
                pointer = pointer.next
            next_head = pointer.next
            pointer.next = None
            return [slice_head, next_head]

        # fill the result
        pointer = head
        current_nodes_seen = 0
        result = []
        using_smaller_size = False
        for i in range(k):
            if not using_smaller_size:
                sublist, next_head = get_slice(pointer, bigger_size)
                current_nodes_seen += bigger_size
            else:
                sublist, next_head = get_slice(pointer, smaller_size)
                current_nodes_seen += smaller_size
            pointer = next_head
            result.append(sublist)
            remaining_buckets = k - len(result)
            remaining_nodes = size - current_nodes_seen
            if remaining_buckets != 0 and (remaining_nodes / remaining_buckets) == smaller_size:
                using_smaller_size = True

        return result