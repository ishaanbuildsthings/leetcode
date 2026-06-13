# live iterating instead of preprocessing, next always goes to the next valid coordinate so it is amortized
class Vector2D:

    def __init__(self, vec: List[List[int]]):
        self.row = 0
        self.col = 0
        self.vec = vec
        while self.row < len(self.vec) and not self.vec[self.row]:
            self.row += 1
        
    

    def next(self) -> int:
        result = self.vec[self.row][self.col]
        currBucket = self.vec[self.row]
        if self.col + 1 < len(currBucket):
            self.col += 1
            return result
        
        while True:
            self.row += 1
            self.col = 0
            if self.row == len(self.vec):
                return result
            if not self.vec[self.row]:
                continue
            return result

            


    def hasNext(self) -> bool:
        if self.row == len(self.vec):
            return False
        return True
        


# Your Vector2D object will be instantiated and called as such:
# obj = Vector2D(vec)
# param_1 = obj.next()
# param_2 = obj.hasNext()