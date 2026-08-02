class Solution:
    def canBeTypedWords(self, text: str, brokenLetters: str) -> int:
        # can be sped up, no space, use a bitmask, etc
        return sum(not any(char in brokenLetters for char in word) for word in text.split(' '))