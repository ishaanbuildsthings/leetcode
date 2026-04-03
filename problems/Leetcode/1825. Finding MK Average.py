from sortedcontainers import SortedList
class MKAverage:

    def __init__(self, m: int, k: int):
        self.mval = m
        self.k = k
        self.l = SortedList()
        self.m = SortedList()
        self.r = SortedList()
        self.q = deque()
        self.mTot = 0

    def addElement(self, num: int) -> None:
        self.q.append(num)
        lost = None
        if len(self.q) > self.mval:
            lost = self.q.popleft()

        if self.l and num <= self.l[-1]:
            self.l.add(num)
        elif self.r and num >= self.r[0]:
            self.r.add(num)
        else:
            self.m.add(num)
            self.mTot += num

        if lost is not None:
            try:
                self.l.remove(lost)
            except:
                try:
                    self.m.remove(lost)
                    self.mTot -= lost
                except:
                    self.r.remove(lost)
        
        while len(self.l) > self.k:
            popped = self.l.pop(-1)
            self.mTot += popped
            self.m.add(popped)
        while len(self.r) > self.k:
            popped = self.r.pop(0)
            self.mTot += popped
            self.m.add(popped)
        while self.m and len(self.l) < self.k:
            popped = self.m.pop(0)
            self.mTot -= popped
            self.l.add(popped)
        while self.m and len(self.r) < self.k:
            popped = self.m.pop(-1)
            self.mTot -= popped
            self.r.add(popped)

    def calculateMKAverage(self) -> int:
        if len(self.q) < self.mval:
            return -1
        return self.mTot // (self.mval - 2 * self.k)
        


# Your MKAverage object will be instantiated and called as such:
# obj = MKAverage(m, k)
# obj.addElement(num)
# param_2 = obj.calculateMKAverage()