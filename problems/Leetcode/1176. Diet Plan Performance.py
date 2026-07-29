class Solution:
    def dietPlanPerformance(self, calories: List[int], k: int, lower: int, upper: int) -> int:
        curr = sum(calories[i] for i in range(k))
        res = -1 if curr < lower else 1 if curr > upper else 0
        for r in range(k, len(calories)):
            curr += calories[r] - calories[r - k]
            res += curr > upper
            res -= curr < lower
        return res
