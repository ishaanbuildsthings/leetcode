class Solution:

    def __init__(self, rects: List[List[int]]):
        self.rects = rects
        self.sizes = []
        for a, b, x, y in rects:
            self.sizes.append((x-a+1)*(y-b+1))
        curr = 0
        self.pf = []
        for size in self.sizes:
            curr += size
            self.pf.append(curr)

    def pick(self) -> List[int]:
        randomPoint = random.randint(1, self.pf[-1])
        # find which rectangle random point occurs in
        l = 0
        r = len(self.pf) - 1
        res = None
        while l <= r:
            m = (r + l) // 2
            accum = self.pf[m]
            if accum >= randomPoint:
                res = m
                r = m - 1
            else:
                l = m + 1
        rect = self.rects[res]
        subtract = self.pf[res - 1] if res else 0
        remain = randomPoint - subtract
        width = rect[2] - rect[0] + 1
        row = (remain - 1) // width
        col = (remain - 1) % width
        return [rect[0] + col, rect[1] + row]


        


# Your Solution object will be instantiated and called as such:
# obj = Solution(rects)
# param_1 = obj.pick()