class OrderedStream:

    def __init__(self, n: int):
        self.bucket = [None] * n
        self.i = 0

    def insert(self, idKey: int, value: str) -> List[str]:
        self.bucket[idKey-1] = value
        res = []
        while self.i < len(self.bucket) and self.bucket[self.i] is not None:
            res.append(self.bucket[self.i])
            self.i += 1
        return res



# Your OrderedStream object will be instantiated and called as such:
# obj = OrderedStream(n)
# param_1 = obj.insert(idKey,value)