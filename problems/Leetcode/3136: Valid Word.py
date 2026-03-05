# https://leetcode.com/problems/valid-word/
# difficulty: easy

# Solution, O(n) time O(1) space, contest solution so it is inefficient

class Solution:
    def isValid(self, word: str) -> bool:
        return (len(word) >= 3 and
        all(char in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in word)
        and any(char in 'aeiouAEIOU' for char in word)
        and any(char not in 'aeiouAEIOU' and not char.isdigit() for char in word)
    )