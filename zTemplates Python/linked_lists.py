# ______________________________________________________________________
# REVERSE PORTION OF LINKED LIST TEMPLATE
# Given a linked list, and a portion l, r, returns the linked list with [l:r] reversed.
def reverse_sublist(head, l, r):
        # find the node before left
        prev = None
        pointer = head
        for _ in range(l):
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

        rev_list_head = reverse_list_and_get_next(pointer, r - l + 1)
        if prev:
            prev.next = rev_list_head
            return head
        return rev_list_head