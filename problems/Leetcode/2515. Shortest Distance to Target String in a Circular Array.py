class Solution:
    def closestTarget(self, words: List[str], target: str, startIndex: int) -> int:

        if words[startIndex] == target:
            return 0
        
        res = inf
        rightmost = -inf
        for i in range(len(words)):
            
            if i == startIndex:
                # dist from left
                distFromLeft = i - rightmost
                res = min(res, distFromLeft)
            if words[i] != target:
                continue
            rightmost = i

        leftmost = inf
        for i in range(len(words) -1, -1, -1):

            if i == startIndex:
                distFromRight = leftmost - i
                res = min(res, distFromRight)
            if words[i] != target:
                continue
            leftmost = i

        # wrap around the left
        distToReach0 = startIndex
        distWrapping = len(words) - rightmost
        wrapLeft = distToReach0+distWrapping

        # wrap around the right
        distToReachEnd = len(words) - startIndex - 1
        distWrapping = leftmost + 1
        wrapRight = distToReachEnd+distWrapping

        res = min(res, wrapLeft, wrapRight)

        return res if res != inf else -1