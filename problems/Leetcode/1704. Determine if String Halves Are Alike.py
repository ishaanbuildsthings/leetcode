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