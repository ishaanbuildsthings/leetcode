class Solution:
    def maxSameLengthRuns(self, s: str) -> int:
        sizes = Counter()
        streak = 1
        for i, c in enumerate(s[1:]):
            if c == s[i]:
                streak += 1
            else:
                sizes[streak] += 1
                streak = 1
        sizes[streak] += 1
        return max(sizes.values())
                