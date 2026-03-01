class Solution:
    def minPartitions(self, n: str) -> int:
        return max(int(char) for char in str(n))
