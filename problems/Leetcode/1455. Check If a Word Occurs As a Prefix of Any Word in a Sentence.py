class Solution:
    def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:
        i = j = spaces = 0
        while i < len(sentence):
            spaces += sentence[i] == ' '
            if sentence[i] == searchWord[j]:
                i += 1
                j += 1
                if j == len(searchWord):
                    return spaces + 1
                continue
            spaces += sentence[i] != ' '
            while i < len(sentence) and sentence[i] != ' ':
                i += 1
            i += 1
            j = 0
        return -1
        

