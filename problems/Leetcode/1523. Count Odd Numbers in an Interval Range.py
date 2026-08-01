class Solution:
    def countOdds(self, low: int, high: int) -> int:
        numbers = high - low + 1
        if low % 2:
            if high % 2:
                return 1 + (numbers // 2)
        return numbers // 2