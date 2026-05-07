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