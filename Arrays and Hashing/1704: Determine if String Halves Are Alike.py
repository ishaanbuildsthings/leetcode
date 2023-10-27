# https://leetcode.com/problems/determine-if-string-halves-are-alike/
# difficulty: easy

# Problem
# You are given a string s of even length. Split this string into two halves of equal lengths, and let a be the first half and b be the second half.

# Two strings are alike if they have the same number of vowels ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'). Notice that s contains uppercase and lowercase letters.

# Return true if a and b are alike. Otherwise, return false.

# Solution, O(n) time and O(1) space
VOWELS_LOWER = ['a', 'e', 'i', 'o', 'u']
class Solution:
    def halvesAreAlike(self, s: str) -> bool:
        vowels = 0
        for i in range(int(len(s) / 2)):
            if s[i].lower() in VOWELS_LOWER:
                vowels += 1
        for j in range(int(len(s) / 2), len(s)):
            if s[j].lower() in VOWELS_LOWER:
                vowels -= 1
                if vowels < 0:
                    return False
        return vowels == 0