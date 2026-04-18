class Solution:
    def checkPerfectNumber(self, num: int) -> bool:
        return sum(
            divisor + num / divisor
            if not num % divisor
            else 0 
            for divisor in range(1, ceil(sqrt(num)))
        ) == 2 * num