class Solution:
    def lateFee(self, daysLate: List[int]) -> int:
        res = 0
        for v in daysLate:
            if v == 1:
                res += 1
            elif v <= 5:
                res += 2 * v
            else:
                res += 3 * v
        
        return res