class Solution:
    def decodeCiphertext(self, encodedText: str, rows: int) -> str:
        n = len(encodedText)
        width = n // rows
        resArr = []
        for i in range(width):
            j = i
            while j < len(encodedText):
                v = encodedText[j]
                resArr.append(v)
                j += width + 1
        return ''.join(resArr).rstrip()
            