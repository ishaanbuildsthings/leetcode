# APPROACH 0, binary search with blacklist, log^2 n

class Solution:

    def __init__(self, m: int, n: int):
        self.black = SortedList()
        self.cells = m * n
        self.m = m
        self.n = n

    def flip(self) -> List[int]:
        iRange = self.cells - len(self.black) - 1 # we go from 0...iRange
        randI = random.randint(0, iRange)
        # binary search for smallest index that would be the fifth element
        l = 0
        r = self.cells - 1
        res = None
        while l <= r:
            m = (l + r) // 2
            cntLte = self.black.bisect_right(m)
            newI = m - cntLte
            if newI < randI:
                l = m + 1
            elif newI == randI:
                res = m
                r = m - 1
            else:
                r = m - 1
        
        trueIdx = res
        row = trueIdx // self.n
        col = trueIdx % self.n
        self.black.add(trueIdx)
        return row, col

        

    def reset(self) -> None:
        self.black = SortedList()


# Your Solution object will be instantiated and called as such:
# obj = Solution(m, n)
# param_1 = obj.flip()
# obj.reset()




# APPROACH 1, O(1) time everything, swapping + virtual array
class Solution:

    def __init__(self, m: int, n: int):
        self.H = m
        self.W = n
        self.empty = m * n - 1 # this is like a tail pointer for next available i in the virtual array
        # we have a virtual array of size m * n
        # it goes from 0...H*W - 1
        self.swapped = {} # maps i -> some empty empty i that took its place

    def flip(self) -> List[int]:
        randI = random.randint(0, self.empty)
        origI = randI
        if randI in self.swapped:
            randI = self.swapped[randI]

        row = randI // self.W
        col = randI % self.W

        idxComingIn = self.empty # we are going to swap in the last free index into randI's place
        # but also if that index position contains something else, we actually use that
        if idxComingIn in self.swapped:
            idxComingIn = self.swapped[idxComingIn]
        
        self.swapped[origI] = idxComingIn

        self.empty -= 1

        return row, col
        


        

    def reset(self) -> None:
        self.swapped = {}
        self.empty = self.H * self.W - 1
        


# Your Solution object will be instantiated and called as such:
# obj = Solution(m, n)
# param_1 = obj.flip()
# obj.reset()