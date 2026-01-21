from sortedcontainers import SortedList

class ModeTracker:
    def __init__(self):
        self.numToFrq = Counter()
        self.frqToNums = defaultdict(lambda: SortedList())
        self.maxFrq = 0
    
    def mode(self):
        return self.frqToNums[self.maxFrq][0]
    
    def add(self, num):
        oldFrq = self.numToFrq[num]
        newFrq = oldFrq + 1
        self.numToFrq[num] = newFrq
        if oldFrq != 0:
            self.frqToNums[oldFrq].remove(num)
        self.frqToNums[newFrq].add(num)
        if newFrq > self.maxFrq:
            self.maxFrq = newFrq
    
    def remove(self, num):
        oldFrq = self.numToFrq[num]
        newFrq = oldFrq - 1
        self.frqToNums[oldFrq].remove(num)
        if newFrq:
            self.frqToNums[newFrq].add(num)
        if not self.frqToNums[oldFrq] and oldFrq == self.maxFrq:
            self.maxFrq -= 1
        self.numToFrq[num] = newFrq
    
    def maxFrqFn(self):
        return self.maxFrq

class Solution:
    def modeWeight(self, nums: List[int], k: int) -> int:

        tracker = ModeTracker()
        res = 0
        for i in range(k):
            tracker.add(nums[i])

        res += tracker.maxFrqFn() * tracker.mode()
        for r in range(k, len(nums)):
            tracker.add(nums[r])
            tracker.remove(nums[r - k])
            res += tracker.maxFrqFn() * tracker.mode()
        
        return res

