class Solution:
    def canPermutePalindrome(self, s: str) -> bool:
        c = Counter(s)
    return sum(c[key] % 2 for key in c) <= 1