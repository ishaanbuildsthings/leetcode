# https://leetcode.com/problems/design-circular-deque/description/
# difficulty: Medium
# tags: deque

# Problem
# Design your implementation of the circular double-ended queue (deque).

# Implement the MyCircularDeque class:

# MyCircularDeque(int k) Initializes the deque with a maximum size of k.
# boolean insertFront() Adds an item at the front of Deque. Returns true if the operation is successful, or false otherwise.
# boolean insertLast() Adds an item at the rear of Deque. Returns true if the operation is successful, or false otherwise.
# boolean deleteFront() Deletes an item from the front of Deque. Returns true if the operation is successful, or false otherwise.
# boolean deleteLast() Deletes an item from the rear of Deque. Returns true if the operation is successful, or false otherwise.
# int getFront() Returns the front item from the Deque. Returns -1 if the deque is empty.
# int getRear() Returns the last item from Deque. Returns -1 if the deque is empty.
# boolean isEmpty() Returns true if the deque is empty, or false otherwise.
# boolean isFull() Returns true if the deque is full, or false otherwise.

# Solution, O(1) everything except O(k) init
# Given we are of size k, we can just allocate an array of that size and use circular pointers. I ended up doing the hashmap implementation though. One note is it might be easier to have self.head = -1, self.tail = 0. They point to head and tail, except when they are crossed. Mine was different, they pointed to where the next insert goes.

class MyCircularDeque:

    def __init__(self, k: int):
        self.data = {}
        self.head = 0 # where the next insertion at the front would go
        self.tail = 0 # where the next insertion at the tail would go
        self.k = k

    def insertFront(self, value: int) -> bool:
        if self.k == self.tail - self.head - 1:
            return False
        self.data[self.head] = value
        if self.head == self.tail:
            self.tail += 1
        self.head -= 1
        return True

    def insertLast(self, value: int) -> bool:
        if self.k == self.tail - self.head - 1:
            return False
        self.data[self.tail] = value
        if self.head == self.tail:
            self.head -= 1
        self.tail += 1
        return True

    def deleteFront(self) -> bool:
        if self.tail - self.head - 1 == -1:
            return False
        self.head += 1
        del self.data[self.head]
        if self.tail == self.head + 1:
            self.tail -= 1
        return True


    def deleteLast(self) -> bool:
        if self.tail - self.head - 1 == -1:
            return False
        self.tail -= 1
        del self.data[self.tail]
        if self.tail == self.head + 1:
            self.head += 1
        return True


    def getFront(self) -> int:
        if self.tail - self.head - 1 == -1:
            return -1
        return self.data[self.head + 1]

    def getRear(self) -> int:
        if self.tail - self.head - 1 == -1:
            return -1
        return self.data[self.tail - 1]

    def isEmpty(self) -> bool:
        return self.tail - self.head - 1 < 0

    def isFull(self) -> bool:
        return self.tail - self.head - 1 == self.k


# Your MyCircularDeque object will be instantiated and called as such:
# obj = MyCircularDeque(k)
# param_1 = obj.insertFront(value)
# param_2 = obj.insertLast(value)
# param_3 = obj.deleteFront()
# param_4 = obj.deleteLast()
# param_5 = obj.getFront()
# param_6 = obj.getRear()
# param_7 = obj.isEmpty()
# param_8 = obj.isFull()