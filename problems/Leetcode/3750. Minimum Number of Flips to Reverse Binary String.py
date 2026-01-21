class Solution:
    def minimumFlips(self, n: int) -> int:
        return sum(
            bin(n)[2:][i] != bin(n)[2:][::-1][i] for i in range(len(bin(n)[2:]))
        )