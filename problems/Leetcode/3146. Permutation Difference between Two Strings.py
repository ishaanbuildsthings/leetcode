class Solution:
    def findPermutationDifference(self, s: str, t: str) -> int:
        return sum(
            abs(s.find(char) - t.find(char)) for char in s
        )