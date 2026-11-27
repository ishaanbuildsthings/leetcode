class Solution:
    def shiftDistance(self, s: str, t: str, nextCost: List[int], previousCost: List[int]) -> int:
        @cache
        def getToRight(aIndex, bIndex):
            if aIndex == bIndex:
                return 0
            costA = nextCost[aIndex]
            return costA + getToRight((aIndex + 1) % 26, bIndex)
        
        @cache
        def getToLeft(aIndex, bIndex):
            if aIndex == bIndex:
                return 0
            costA = previousCost[aIndex]
            newPrev = aIndex - 1 if aIndex > 0 else 25
            return costA + getToLeft(newPrev, bIndex)
        
        res = 0
        for i in range(len(s)):
            a = s[i]
            target = t[i]
            indexA = ord(a) - ord('a')
            indexB = ord(target) - ord('a')
            right = getToRight(indexA, indexB)
            left = getToLeft(indexA, indexB)
            res += min(left, right)
        
        return res