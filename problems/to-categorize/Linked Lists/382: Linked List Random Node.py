# https://leetcode.com/problems/linked-list-random-node/
# difficulty: medium
# tags: linked list

# Problem
# Given a singly linked list, return a random node's value from the linked list. Each node must have the same probability of being chosen.

# Implement the Solution class:

# Solution(ListNode head) Initializes the object with the head of the singly-linked list head.
# int getRandom() Chooses a node randomly from the list and returns its value. All the nodes of the list should be equally likely to be chosen.

# Solution, O(n) time and space init, O(1) time and space random, though there is a cool solution called reservoir sampling

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:

    def __init__(self, head: Optional[ListNode]):
        self.size = -1
        self.vals = {}
        curr = head
        while curr:
            self.vals[self.size + 1] = curr.val
            curr = curr.next
            self.size += 1

    def getRandom(self) -> int:
        randIndex = random.randint(0, self.size)
        return self.vals[randIndex]


# Your Solution object will be instantiated and called as such:
# obj = Solution(head)
# param_1 = obj.getRandom()