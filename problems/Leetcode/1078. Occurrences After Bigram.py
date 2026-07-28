class Solution:
    def findOcurrences(self, text: str, first: str, second: str) -> List[str]:
        # can do in O(1) space
        splitText = text.split(' ')
        res = []

        # can operationally optimize this lol
        for i in range(2, len(splitText)):
            if splitText[i - 2] == first and splitText[i - 1] == second:
                res.append(splitText[i])
        return res