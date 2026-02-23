class Solution:
    def minSumSquareDiff(self, nums1: List[int], nums2: List[int], k1: int, k2: int) -> int:
        n = len(nums1)
        ops = k1 + k2
        diffs = [abs(nums1[i] - nums2[i]) for i in range(n)]
        diffs.sort(reverse=True)
        diffs.append(0)

        setI = 0

        for i in range(1, n + 1):
            prevCount = i
            prevV = diffs[i - 1]
            fall = diffs[i - 1] - diffs[i]
            totalOpsNeeded = fall * prevCount
            # if we can set everything to this value
            if totalOpsNeeded <= ops:
                ops -= totalOpsNeeded
                setI = i
                continue
            
            # if we cannot set everything to this value
            opsDroppedPerPrev = ops // prevCount
            remainOps = ops - (opsDroppedPerPrev * prevCount)

            # score from this number onwards
            score = 0
            for j in range(i, n):
                score += diffs[j]**2
                        
            prevHighCount = prevCount - remainOps # remainOps is basically the low count
            highVal = diffs[i - 1] - opsDroppedPerPrev
            score += prevHighCount * highVal**2
            lowVal = highVal - 1
            score += remainOps * lowVal**2

            
            return score
        
        return 0