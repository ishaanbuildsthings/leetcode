class Solution:
    def findPoisonedDuration(self, timeSeries: List[int], duration: int) -> int:
        res = left = right = 0
        for t in timeSeries:
            if right >= t:
                right = max(right, t + duration)
            else:
                res += right - left
                left = t
                right = t + duration
        res += right - left
        return res




