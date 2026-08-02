class Solution:
    def sortSentence(self, s: str) -> str:
        words = 1 + sum(s[i] == ' ' for i in range(len(s)))
        resArr = [None] * words
        for word in s.split(' '):
            pos = int(word[-1]) - 1
            start = word[:-1]
            resArr[pos] = start
        return ' '.join(resArr)