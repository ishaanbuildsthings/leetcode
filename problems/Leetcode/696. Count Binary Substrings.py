class Solution:
    def countBinarySubstrings(self, s: str) -> int:
        # can do O(1) space
        
        groups = [len(list(g)) for _, g in groupby(s)]
        return sum(
            min(groups[i], groups[i + 1]) for i in range(len(groups) - 1)
        )