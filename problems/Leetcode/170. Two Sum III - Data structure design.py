from sortedcontainers import SortedList

class TwoSum:

    # can use counter to filter triple occurences
    def __init__(self):
        self.x = SortedList()
        self.c = Counter()
        # self.vals = []

    def add(self, number: int) -> None:
        if self.c[number] == 2:
            return
        self.c[number] += 1
        self.x.add(number)
        # self.vals.append(number)

    def find(self, value: int) -> bool:
        l = 0
        r = len(self.x) - 1
        while l < r:
            tot = self.x[l] + self.x[r]
            if tot == value:
                return True
            elif tot < value:
                l += 1
            else:
                r -= 1
        return False
        # for i in range(len(self.vals) - 1):
        #     for j in range(i + 1, len(self.vals)):
        #         if self.vals[i] + self.vals[j] == value:
        #             return True
        # return False


# Your TwoSum object will be instantiated and called as such:
# obj = TwoSum()
# obj.add(number)
# param_2 = obj.find(value)