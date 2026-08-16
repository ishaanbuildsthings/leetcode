class FreqStack:

    def __init__(self):
        self.t = 0
        self.heap = []
        self.frq = defaultdict(int)

    def push(self, val: int) -> None:
        self.frq[val] += 1
        heapq.heappush(self.heap, (-self.frq[val], -self.t, val))
        self.t += 1

    def pop(self) -> int:
        while self.heap:
            poppedFrq, t, v = heapq.heappop(self.heap)
            poppedFrq *= -1
            t *= -1
            if poppedFrq != self.frq[v]:
                continue
            self.frq[v] -= 1
            return v
        


# Your FreqStack object will be instantiated and called as such:
# obj = FreqStack()
# obj.push(val)
# param_2 = obj.pop()