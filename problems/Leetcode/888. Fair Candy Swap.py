class Solution:
    def fairCandySwap(self, aliceSizes: List[int], bobSizes: List[int]) -> List[int]:
        t1 = sum(aliceSizes)
        t2 = sum(bobSizes)
        bobSet = set(bobSizes)
        aSurplus = t1 - t2 # we need to lose this much from alice, say 2
        for v in aliceSizes:
            reqSmaller = int(v - (aSurplus / 2))
            if reqSmaller in bobSet:
                return [v, reqSmaller]