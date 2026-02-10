class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        res = l = r = 0
        inWindow = set() # characters in current window
        while r < len(s):
            gainedLetter = s[r]
            while gainedLetter in inWindow:
                lostLetter = s[l]
                inWindow.remove(lostLetter)
                l += 1
            inWindow.add(gainedLetter)
            res = max(res, r - l + 1)
            r += 1
        return res