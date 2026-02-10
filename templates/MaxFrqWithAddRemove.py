# O(1) add a number to the structure
# O(1) remove a number from structure
# O(1) find max frequency of an element

# It works by mapping:
# number -> frequency
# frequency -> list of numbers

# When we pop an element the old bucket of numbers with that frequency needs updating, we can do it in O(1) by swapping that with the last element of the array
# then popping (swap and pop trick), but this requires tracking the position of every element in the buckets too

# If we don't want that, we can just track a number -> frequency and a frequency -> count of numbers, easier to implement but now we can't get all numbers of a given frequency
from collections import defaultdict

class MaxFrequencyStructure:
    def __init__(self):
        self.valueToFreq = defaultdict(int)
        self.valueToIndex = {}
        self.freqToValues = defaultdict(list)
        self.maxFreq = 0

    def getMaxFrequency(self):
        return self.maxFreq

    def getValuesWithMaxFrequency(self):
        return self.freqToValues[self.maxFreq]

    def push(self, value):
        oldFreq = self.valueToFreq[value]
        newFreq = oldFreq + 1
        self.valueToFreq[value] = newFreq

        if oldFreq > 0:
            self._removeFromBucket(value, oldFreq)

        self._addToBucket(value, newFreq)

        if newFreq > self.maxFreq:
            self.maxFreq = newFreq

    def pop(self, value):
        oldFreq = self.valueToFreq[value]
        newFreq = oldFreq - 1
        self.valueToFreq[value] = newFreq

        self._removeFromBucket(value, oldFreq)

        if newFreq > 0:
            self._addToBucket(value, newFreq)
        else:
            del self.valueToIndex[value]

        while self.maxFreq > 0 and not self.freqToValues[self.maxFreq]:
            self.maxFreq -= 1

    def _addToBucket(self, value, freq):
        bucket = self.freqToValues[freq]
        self.valueToIndex[value] = len(bucket)
        bucket.append(value)

    def _removeFromBucket(self, value, freq):
        bucket = self.freqToValues[freq]
        i = self.valueToIndex[value]
        lastValue = bucket[-1]
        bucket[i] = lastValue
        self.valueToIndex[lastValue] = i
        bucket.pop()
