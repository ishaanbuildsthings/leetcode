# https://leetcode.com/problems/moving-average-from-data-stream/description/
# difficulty: easy
# tags: deque

# Problem
# Given a stream of integers and a window size, calculate the moving average of all integers in the sliding window.

# Implement the MovingAverage class:

# MovingAverage(int size) Initializes the object with the size of the window size.
# double next(int val) Returns the moving average of the last size values of the stream.

# Solution, O(1) time and space for init and next, but O(size) eventual space once we fill the structure, standard deque with popleft as we need to know what gets dequeued

class MovingAverage:

    def __init__(self, size: int):
        self.storage = collections.deque()
        self.size = size
        self.sum = 0

    def next(self, val: int) -> float:
        if len(self.storage) == self.size:
            lost = self.storage.popleft()
            self.sum -= lost
        self.storage.append(val)
        self.sum += val
        return self.sum / len(self.storage)




# Your MovingAverage object will be instantiated and called as such:
# obj = MovingAverage(size)
# param_1 = obj.next(val)