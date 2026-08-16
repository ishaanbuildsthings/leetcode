# https://leetcode.com/problems/maximum-frequency-stack/
# difficulty: hard
# tags: stack, avl tree

# Problem
# Design a stack-like data structure to push elements to the stack and pop the most frequent element from the stack.

# Implement the FreqStack class:

# FreqStack() constructs an empty frequency stack.
# void push(int val) pushes an integer val onto the top of the stack.
# int pop() removes and returns the most frequent element in the stack.
# If there is a tie for the most frequent element, the element closest to the stack's top is removed and returned.

# Solution
# I kept an AVL of AVLs. So the outer avl maps [value, frequency, inner AVL] and each inner AVL is an AVL of the indices. A stack of stacks is better and the recommended solution though.

from sortedcontainers import SortedList

class FreqStack:

    def __init__(self):
        self.counter = -1 # increases each push
        self.outerAVL = SortedList(key=lambda x: (-1 * x[1], -1 * x[2][-1])) # stores [value, frequency, inner AVL]. Sorts by largest frequencies first, then by the biggest / topmost element in the inner AVL. The inner AVL stores a list of counters.
        self.hashmap = {} # maps a value to the relevant [value, frequency, inner AVL]

    def push(self, val: int) -> None:
        self.counter += 1
        if val in self.hashmap:
            tup = self.hashmap[val]
            self.outerAVL.remove(tup)  # Remove the tuple from outerAVL
            _, frq, innerAVL = tup
            tup[1] += 1 # increase frequency
            innerAVL.add(self.counter)
            self.outerAVL.add(tup)  # Re-add the modified tuple to outerAVL

        else:
            innerAVL = SortedList()
            tup = [val, 1, innerAVL]
            self.hashmap[val] = tup
            innerAVL.add(self.counter)
            self.outerAVL.add(tup)

    def pop(self) -> int:

        # Remove the tuple from outerAVL
        tup = self.outerAVL.pop(0)
        val, frq, innerAVL = tup
        tup[1] -= 1
        innerAVL.pop(-1)
        if tup[1] != 0:
            self.outerAVL.add(tup)
        else:
            del self.hashmap[val]

        return val



# Your FreqStack object will be instantiated and called as such:
# obj = FreqStack()
# obj.push(val)
# param_2 = obj.pop()