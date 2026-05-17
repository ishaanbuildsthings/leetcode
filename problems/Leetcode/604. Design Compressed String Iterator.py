class StringIterator:

    def __init__(self, compressedString: str):
        self.i = 0
        self.completed = 0
        self.buckets = [] # (letter, amount)
        i = 0
        while i < len(compressedString):
            letter = compressedString[i]
            num = []
            for j in range(i + 1, len(compressedString)):
                if compressedString[j].isalpha():
                    break
                num.append(compressedString[j])
            num = int(''.join(num))
            i = j if j != len(compressedString) - 1 else len(compressedString)
            self.buckets.append((letter, num))

    def next(self) -> str:
        if not self.hasNext():
            return ' '
        letter, fullAmount = self.buckets[self.i]
        self.completed += 1
        if self.completed == fullAmount:
            self.i += 1
            self.completed = 0
        return letter
        

    def hasNext(self) -> bool:
        return self.i < len(self.buckets)
        


# Your StringIterator object will be instantiated and called as such:
# obj = StringIterator(compressedString)
# param_1 = obj.next()
# param_2 = obj.hasNext()