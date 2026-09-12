abc = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def minSteps(self, s: str, t: str) -> int:
        counts1 = Counter(s)
        counts2 = Counter(t)

        return sum(
            abs(counts1[char] - counts2[char])
            for char in abc
        )