class Solution:
    def countLetters(self, s: str) -> int:
        res = 0
        curr = None
        size = 0
        for char in s:
            if char == curr:
                size += 1
            else:
                curr = char
                size = 1
            res += size
        return res