class Solution:
    def countGoodRectangles(self, rectangles: List[List[int]]) -> int:
        res = 0
        bigSide = 0
        for l, w in rectangles:
            bigSideHere = min(l, w)
            res += bigSide == bigSideHere
            if bigSideHere > bigSide:
                bigSide = bigSideHere
                res = 1
        return res