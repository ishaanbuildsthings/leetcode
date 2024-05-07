# https://leetcode.com/problems/reverse-prefix-of-word/description/?envType=daily-question&envId=2024-05-01
# difficulty: easy

# Solution, O(n) time O(n) space

class Solution:
    def reversePrefix(self, word: str, ch: str) -> str:
        for i, char in enumerate(word):
            if char == ch:
                before = word[i::-1]
                after = word[i+1:]
                return before + after
        return word