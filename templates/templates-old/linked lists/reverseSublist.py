# ______________________________________________________________________
# TEMPLATE
# REVERSE PORTION OF LINKED LIST
# Given a linked list, and a portion l, r, returns the linked list with [l:r] reversed.
def reverseSublist(head, l, r):
        # find the node before left
        prev = None
        pointer = head
        for _ in range(l):
            prev = pointer
            pointer = pointer.next

        def reverseListAndGetNext(linkedList, reverseSize):
            newTail = linkedList
            pointer = linkedList
            prev = None
            for i in range(reverseSize):
                next_node = pointer.next
                pointer.next = prev
                prev = pointer
                pointer = next_node
            newTail.next = pointer
            return prev

        revListHead = reverseListAndGetNext(pointer, r - l + 1)
        if prev:
            prev.next = revListHead
            return head
        return revListHead