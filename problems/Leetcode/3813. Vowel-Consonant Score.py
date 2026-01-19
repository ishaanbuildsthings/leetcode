class Solution:
    def vowelConsonantScore(self, s: str) -> int:
        v = sum(x in 'aeiou' for x in s)
        c = sum(x.isalpha() and x not in 'aeiou' for x in s)
        if c == 0:
            return 0
        return v // c