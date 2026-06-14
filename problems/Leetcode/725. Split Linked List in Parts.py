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