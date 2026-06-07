class Solution:
    def countBits(self, n: int) -> List[int]:
        return [num.bit_count() for num in range(n + 1)]