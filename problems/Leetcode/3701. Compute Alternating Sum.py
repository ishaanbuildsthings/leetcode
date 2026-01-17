class Solution:
    def alternatingSum(self, a: List[int]) -> int:
        return sum(a[i] if i % 2 == 0 else -a[i] for i in range(len(a)))