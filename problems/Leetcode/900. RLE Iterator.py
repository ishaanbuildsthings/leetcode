class RLEIterator:

    def __init__(self, encoding: List[int]):
        self.enc = encoding
        self.cntI = 0

    def next(self, n: int) -> int:
        remain = n
        for _ in range(n):
            if self.cntI >= len(self.enc):
                return -1
            while self.enc[self.cntI] == 0:
                self.cntI += 2
                if self.cntI >= len(self.enc):
                    return -1
            burned = min(remain, self.enc[self.cntI])
            remain -= burned
            self.enc[self.cntI] -= burned
            if not remain:
                return self.enc[self.cntI + 1]
        
        return -1

        


# Your RLEIterator object will be instantiated and called as such:
# obj = RLEIterator(encoding)
# param_1 = obj.next(n)