class RandomizedCollection:

    def __init__(self):
        self.c = Counter()
        self.arr = []
        self.lazyDelete = Counter()

    def insert(self, val: int) -> bool:
        self.c[val] += 1
        res = self.c[val] == 1
        self.arr.append(val)
        return res


    def remove(self, val: int) -> bool:
        if not self.c[val]:
            return False
        self.c[val] -= 1
        self.lazyDelete[val] += 1
        return True

    def getRandom(self) -> int:
        while True:
            randomIndex = random.randint(0, len(self.arr) - 1)
            randVal = self.arr[randomIndex]
            if self.lazyDelete[randVal]:
                self.lazyDelete[randVal] -= 1
                self.arr[randomIndex], self.arr[-1] = self.arr[-1], self.arr[randomIndex]
                self.arr.pop()
                continue
            return randVal
            



# Your RandomizedCollection object will be instantiated and called as such:
# obj = RandomizedCollection()
# param_1 = obj.insert(val)
# param_2 = obj.remove(val)
# param_3 = obj.getRandom()