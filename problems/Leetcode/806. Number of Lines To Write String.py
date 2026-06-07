class Solution:
    def numberOfLines(self, widths: List[int], s: str) -> List[int]:
        currWidth = 0
        lines = 1
        def charToWidth(char):
            idx = ord(char) - ord('a')
            return widths[idx]
        for c in s:
            width = charToWidth(c)
            if currWidth + width <= 100:
                currWidth += width
            else:
                currWidth = width
                lines += 1
        return [lines, currWidth]