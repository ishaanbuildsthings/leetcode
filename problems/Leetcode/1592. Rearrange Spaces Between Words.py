class Solution:
    def reorderSpaces(self, text: str) -> str:
        words = text.split(' ')
        words = [w for w in words if w != '']
        
        spaces = sum(c == ' ' for c in text)
        wordCount = len(words)
        spots = wordCount - 1
        spacesPerSpot = (spaces // spots) if spots else 0
        endSpaces = spaces % spots if spaces and spots else spaces if not spots else 0

        resArr = []
        for w in words:
            resArr.append(w)
            resArr.append(' ' * spacesPerSpot)
        resArr.pop()
        resArr.append(' ' * endSpaces)
        return ''.join(resArr)