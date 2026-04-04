class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, val, id):
        heapq.heappush(self.heap, (-val, -id))

    def pop(self):
        val, id = heapq.heappop(self.heap)
        return -val, -id

    def peek(self):
        return -self.heap[0][0], -self.heap[0][1]

class MaxStack:

    def __init__(self):
        self.maxHeap = MaxHeap()
        self.stack = []
        self.removed = set()
        self.cnt = 0

    def push(self, x: int) -> None:
        self.stack.append((x, self.cnt))
        self.maxHeap.push(x, self.cnt)
        self.cnt += 1

    def pop(self) -> int:
        while self.stack[-1][1] in self.removed:
            self.removed.discard(self.stack[-1][1])
            self.stack.pop()
        val, id = self.stack.pop()
        self.removed.add(id)
        return val

    def top(self) -> int:
        while self.stack[-1][1] in self.removed:
            self.removed.discard(self.stack[-1][1])
            self.stack.pop()
        return self.stack[-1][0]

    def peekMax(self) -> int:
        while self.maxHeap.peek()[1] in self.removed:
            self.removed.discard(self.maxHeap.pop()[1])
        return self.maxHeap.peek()[0]

    def popMax(self) -> int:
        while self.maxHeap.peek()[1] in self.removed:
            self.removed.discard(self.maxHeap.pop()[1])
        val, id = self.maxHeap.pop()
        self.removed.add(id)
        return val

# Your MaxStack object will be instantiated and called as such:
# obj = MaxStack()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.top()
# param_4 = obj.peekMax()
# param_5 = obj.popMax()