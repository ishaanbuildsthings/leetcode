class Solution:
    def freqAlphabets(self, s: str) -> str:
        def strNumToChar(strNum):
            return chr(int(strNum) + ord('a') - 1)

        resArr = []
        i = 0
        while i < len(s):
            if i < len(s) - 2 and s[i+2] == '#':
                resArr.append(strNumToChar(s[i:i+2]))
                i += 3
            else:
                resArr.append(strNumToChar(s[i]))
                i += 1

        return ''.join(resArr)

