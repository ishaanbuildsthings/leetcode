class Solution:
    def constructRectangle(self, area: int) -> List[int]:
        # can start from rootN and go down
        for factor in range(1, math.ceil(math.sqrt(area)) + 1):
            if not area % factor == 0:
                continue
            f1 = factor
            f2 = area // f1
            res = [max(f1,f2),min(f1,f2)]
        return res
