# https://leetcode.com/problems/design-a-number-container-system/description/
# Difficulty: Medium
# tags: avl tree

# Problem
# Design a number container system that can do the following:

# Insert or Replace a number at the given index in the system.
# Return the smallest index for the given number in the system.
# Implement the NumberContainers class:

# NumberContainers() Initializes the number container system.
# void change(int index, int number) Fills the container at index with the number. If there is already a number at that index, replace it.
# int find(int number) Returns the smallest index for the given number, or -1 if there is no index that is filled by number in the system.

# Solution, O(1) find, O(log n) change
# Maintain a map of an index to a number. And maintain a map of a number to an AVL of its indices. When we insert or replace, we remove the old index from the AVL and add the new index to the AVL. When we find, we return the smallest index in the AVL. Also update the index to number map.

from sortedcontainers import SortedList

class NumberContainers:

    def __init__(self):
        self.mapping = defaultdict(lambda: SortedList()) # each number contains a sorted list of its indices
        self.indicesMapping = {} # maps an index to a number

    def change(self, index: int, number: int) -> None:
        priorNumber = self.indicesMapping[index] if index in self.indicesMapping else None
        self.indicesMapping[index] = number
        if priorNumber != None:
            self.mapping[priorNumber].remove(index)
        self.mapping[number].add(index)

    def find(self, number: int) -> int:
        return self.mapping[number][0] if len(self.mapping[number]) else -1


# Your NumberContainers object will be instantiated and called as such:
# obj = NumberContainers()
# obj.change(index,number)
# param_2 = obj.find(number)