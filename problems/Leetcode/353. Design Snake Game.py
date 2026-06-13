class SnakeGame:

    def __init__(self, width: int, height: int, food: List[List[int]]):
        self.occupied = deque()
        self.occupied.append((0, 0))
        self.occSet = {(0, 0)}
        self.food = food
        self.foodI = 0
        self.height = height
        self.width = width

    def move(self, direction: str) -> int:
        currR = self.occupied[-1][0]
        currC = self.occupied[-1][1]
        
        dirToTup = {
            'U' : (-1, 0),
            'D' : (1, 0),
            'L' : (0, -1),
            'R' : (0, 1)
        }

        nR, nC = currR + dirToTup[direction][0], currC + dirToTup[direction][1]

        # handle out of bounds
        if nR < 0 or nC < 0 or nR == self.height or nC == self.width:
            return -1
        
        # if we ate a food, we only gain a new position
        if self.foodI < len(self.food) and self.food[self.foodI][0] == nR and self.food[self.foodI][1] == nC:
            # but if we already were in that position, we lose
            if (nR, nC) in self.occSet:
                return -1
            self.occSet.add((nR, nC))
            self.occupied.append((nR, nC))
            self.foodI += 1
        
        # if we didn't eat a food, pop the last location
        else:
            tail = self.occupied[0]
            tailR, tailC = tail
            self.occSet.remove((tailR, tailC))
            self.occupied.popleft()
            # but if we are in that last location after tail pop, we lose
            if (nR, nC) in self.occSet:
                return -1
            self.occupied.append((nR, nC))
            self.occSet.add((nR, nC))
        
        return self.foodI



# Your SnakeGame object will be instantiated and called as such:
# obj = SnakeGame(width, height, food)
# param_1 = obj.move(direction)