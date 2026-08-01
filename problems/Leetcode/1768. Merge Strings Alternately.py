class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        resArr = []
        a = b = 0
        while a < len(word1) and b < len(word2):
            resArr.append(word1[a])
            resArr.append(word2[b])
            a += 1
            b += 1
        while a < len(word1):
            resArr.append(word1[a])
            a += 1
        while b < len(word2):
            resArr.append(word2[b])
            b += 1
        return ''.join(resArr)