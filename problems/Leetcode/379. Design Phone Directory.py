from sortedcontainers import SortedList
class PhoneDirectory:

    def __init__(self, maxNumbers: int):
        self.sl = SortedList() # stores used numbers
        self.mx = maxNumbers - 1 # we have 0...maxNumbers-1

    def get(self) -> int:
        # find the largest used number s.t. we have used all 0...X
        l = 0
        r = len(self.sl) - 1
        res = None
        while l <= r:
            m = (r+l)//2
            v = self.sl[m]
            if v == m:
                res = m
                l = m + 1
            else:
                r = m - 1
        if res is None:
            self.sl.add(0)
            return 0
        nfree = res + 1
        if nfree > self.mx:
            return -1
        self.sl.add(nfree)
        return nfree

    def check(self, number: int) -> bool:
        return number not in self.sl
        

    def release(self, number: int) -> None:
        self.sl.discard(number)
        


# Your PhoneDirectory object will be instantiated and called as such:
# obj = PhoneDirectory(maxNumbers)
# param_1 = obj.get()
# param_2 = obj.check(number)
# obj.release(number)