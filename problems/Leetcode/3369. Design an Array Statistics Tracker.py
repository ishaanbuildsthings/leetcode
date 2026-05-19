from sortedcontainers import SortedList
class StatisticsTracker:

    def __init__(self):
        self.tot = 0
        self.items = SortedList()
        self.q = deque()
        self.frqs = Counter()
        self.freqAndItem = SortedList(key=lambda x: (-x[0], x[1])) # holds (frequency, item) with sorted biggest frequency first, smallest item first

    def addNumber(self, number: int) -> None:
        self.tot += number
        oldFrq = self.frqs[number]
        self.frqs[number] += 1

        if oldFrq:
            oldTup = (oldFrq, number)
            self.freqAndItem.remove(oldTup)
        newTup = (oldFrq + 1, number)
        self.freqAndItem.add(newTup)

        self.items.add(number)
        self.q.append(number)

    def removeFirstAddedNumber(self) -> None:
        firstElement = self.q[0]
        self.q.popleft()
        self.items.remove(firstElement)
        self.tot -= firstElement

        oldFrq = self.frqs[firstElement]
        self.frqs[firstElement] -= 1

        oldTup = (oldFrq, firstElement)
        self.freqAndItem.remove(oldTup)
        newFreq = oldFrq - 1
        if newFreq:
            self.freqAndItem.add((newFreq, firstElement))

    def getMean(self) -> int:
        return self.tot // len(self.items)

    def getMedian(self) -> int:
        return self.items[len(self.items) // 2]

    def getMode(self) -> int:
        return self.freqAndItem[0][1]


# Your StatisticsTracker object will be instantiated and called as such:
# obj = StatisticsTracker()
# obj.addNumber(number)
# obj.removeFirstAddedNumber()
# param_3 = obj.getMean()
# param_4 = obj.getMedian()
# param_5 = obj.getMode()