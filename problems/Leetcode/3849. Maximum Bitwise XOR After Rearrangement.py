class Solution:
    def maximumXor(self, s: str, t: str) -> str:
        n = len(s)
        tCount = Counter(t)
        resArr = [None] * n
        for i in range(n):
            if s[i] == '1':
                if tCount['0']:
                    tCount['0'] -= 1
                    resArr[i] = '1'
                else:
                    tCount['1'] -= 1
                    resArr[i] = '0'
            else:
                if tCount['1']:
                    tCount['1'] -= 1
                    resArr[i] = '1'
                else:
                    tCount['0'] -= 1
                    resArr[i] = '0'
        return ''.join(resArr)