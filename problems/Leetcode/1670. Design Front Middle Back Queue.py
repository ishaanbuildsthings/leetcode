class FrontMiddleBackQueue:

    def __init__(self):
        self.l = deque() # always <= r size
        self.r = deque()
    
    def _rebalance(self):
        # L too big
        while len(self.l) > len(self.r):
            self.r.appendleft(self.l.pop())
        # R too big
        while len(self.r) > len(self.l) + 1:
            self.l.append(self.r.popleft())
        # L too small
        while len(self.l) < len(self.r) - 1:
            self.l.append(self.r.popleft())
        # R too small
        while len(self.r) < len(self.l):
            self.r.appendleft(self.l.pop())

    def pushFront(self, val: int) -> None:
        self.l.appendleft(val)
        self._rebalance()

    def pushMiddle(self, val: int) -> None:
        self.l.append(val)
        self._rebalance()
        

    def pushBack(self, val: int) -> None:
        self.r.append(val)
        self._rebalance()

    def popFront(self) -> int:
        if not self.r:
            return -1
        ans = self.l.popleft() if self.l else self.r.popleft()
        self._rebalance()
        return ans
        

    def popMiddle(self) -> int:
        if not self.r and not self.l:
            return -1
        if len(self.l) < len(self.r):
            ans = self.r.popleft()
            self._rebalance()
            return ans
        else:
            ans = self.l.pop()
            self._rebalance()
            return ans

    def popBack(self) -> int:
        if not self.r:
            return -1
        ans = self.r.pop()
        self._rebalance()
        return ans
        


# Your FrontMiddleBackQueue object will be instantiated and called as such:
# obj = FrontMiddleBackQueue()
# obj.pushFront(val)
# obj.pushMiddle(val)
# obj.pushBack(val)
# param_4 = obj.popFront()
# param_5 = obj.popMiddle()
# param_6 = obj.popBack()