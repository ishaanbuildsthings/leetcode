class FrequencyTracker:

    def __init__(self):
        self.nums = defaultdict(int) # maps a num to its frq
        self.frqs = defaultdict(set) # maps a frq to a set of numbers with that frequency

    def add(self, number: int) -> None:
        prevFrq = self.nums[number]
        self.nums[number] += 1
        self.frqs[prevFrq].discard(number)
        self.frqs[prevFrq + 1].add(number)

    def deleteOne(self, number: int) -> None:
        prevFrq = self.nums[number]
        if (self.nums[number] != 0):
            self.nums[number] -= 1
        self.frqs[prevFrq].discard(number)
        self.frqs[prevFrq - 1].add(number)
        

    def hasFrequency(self, frequency: int) -> bool:
        return len(self.frqs[frequency])


# Your FrequencyTracker object will be instantiated and called as such:
# obj = FrequencyTracker()
# obj.add(number)
# obj.deleteOne(number)
# param_3 = obj.hasFrequency(frequency)