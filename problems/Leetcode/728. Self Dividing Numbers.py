class Solution:
    def selfDividingNumbers(self, left: int, right: int) -> List[int]:
        return [
            num for num in range(left, right + 1) if all(
                int(c) and num % int(c) == 0 for c in str(num)
            )
        ]