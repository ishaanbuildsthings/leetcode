class Solution:
    def generateTheString(self, n: int) -> str:
        if n % 2:
            return 'a' * n
        return 'b' + ('a' * (n - 1))