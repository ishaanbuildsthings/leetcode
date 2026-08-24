class Solution:
    def decodeMessage(self, key: str, message: str) -> str:
        subTable = ''
        seen = set()
        for c in key:
            if c in seen:
                continue
            if c == ' ':
                continue
            subTable += c
            seen.add(c)
        
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        letterToIdx = {
            letter : i for i, letter in enumerate(subTable)
        }
        return ''.join([ABC[letterToIdx[letter]] if letter != ' ' else ' ' for letter in message])
        
