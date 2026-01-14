class RangeSumQuery1d:
    def __init__(self, iterable):
        self.runningSum = 0
        self.prefixSums = []
        for num in iterable:
            self.runningSum += num
            self.prefixSums.append(self.runningSum)

    def sumQuery(self, l, r):
        if l == 0:
            return self.prefixSums[r]
        return self.prefixSums[r] - self.prefixSums[l - 1]





