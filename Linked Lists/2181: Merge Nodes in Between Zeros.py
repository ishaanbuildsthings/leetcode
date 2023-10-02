# https://leetcode.com/problems/merge-nodes-in-between-zeros/
# difficulty: medium
# tags: linked lists

# problem
# You are given the head of a linked list, which contains a series of integers separated by 0's. The beginning and end of the linked list will have Node.val == 0.

# For every two consecutive 0's, merge all the nodes lying in between them into a single node whose value is the sum of all the merged nodes. The modified list should not contain any 0's.

# Return the head of the modified linked list.

# Solution, O(n) time and O(1) space, since we aren't really modifying the list (though I guess there is a difference in modifying a node since it may be referenced elsewhere), I ended up just creating a new list

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(None)
        tail = dummy
        pointer = head.next
        runningSum = 0
        while pointer:
            if pointer.val == 0:
                tail.next = ListNode(runningSum)
                tail = tail.next
                runningSum = 0
            runningSum += pointer.val
            pointer = pointer.next
        return dummy.next
