class Solution:
    def countArrays(self, original: List[int], bounds: List[List[int]]) -> int:
        res = inf
        prevL, prevR = bounds[0][0], bounds[0][1]

        for i in range(1, len(original)):
            diff = original[i] - original[i-1]
            l, r = bounds[i]
            newL = max(prevL+diff,l)
            newR = min(prevR+diff,r)
            res = min(res, newR-newL+1)
            prevL, prevR = newL, newR
        
        return max(res, 0)