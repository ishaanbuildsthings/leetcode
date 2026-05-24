class Solution:
    def reverseStr(self, s: str, k: int) -> str:
        resArr = []
        parity = 1
        for i in range(0, len(s), k):
            if parity == 0:
                resArr.append(s[i:i+k])
                parity ^= 1
            else:
                resArr.append(s[i:i+k][::-1])
                parity ^= 1
        return ''.join(resArr)
            
            