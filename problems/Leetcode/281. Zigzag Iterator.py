class ZigzagIterator:
    def __init__(self, v1: List[int], v2: List[int]):
        self.i1 = 0
        self.i2 = 0
        self.a = v1
        self.b = v2
        self.curr = 0

    def next(self) -> int:
        # edge case for empty array
        if self.curr == 0 and self.i1 == len(self.a):
            ans = self.b[self.i2]
            self.i2 += 1
            self.curr = 1
            return ans
        if self.curr == 1 and self.i2 == len(self.b):
            ans = self.a[self.i1]
            self.i1 += 1
            self.curr = 0
            return ans

        if self.curr == 0:
            ans = self.a[self.i1]
            self.i1 += 1
            # can use another element from the next array
            if self.i2 < len(self.b):
                self.curr = 1
        else:
            ans = self.b[self.i2]
            self.i2 += 1
            if self.i1 < len(self.a):
                self.curr = 0
        return ans
        

    def hasNext(self) -> bool:
        return self.i1 < len(self.a) or self.i2 < len(self.b)

# Your ZigzagIterator object will be instantiated and called as such:
# i, v = ZigzagIterator(v1, v2), []
# while i.hasNext(): v.append(i.next())