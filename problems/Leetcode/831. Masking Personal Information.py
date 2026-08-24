class Solution:
    def maskPII(self, s: str) -> str:
        # email
        if '@' in s:
            resArr = []
            splitPoint = s.index('@')
            resArr.append(s[0].lower())
            resArr.extend(['*'] * 5)
            resArr.append(s[splitPoint - 1].lower())
            
            for j in range(splitPoint, len(s)):
                resArr.append(s[j].lower())
            return ''.join(resArr)
        
        # phone
        resArr = [char for char in s if not char in ['+', '-', '(', ')', ' ']]
        lastFour = ''.join(resArr[-4:])
        base = '***-***-' + lastFour
        if len(resArr) == 10:
            return base
        elif len(resArr) == 11:
            return '+*-' + base
        elif len(resArr) == 12:
            return '+**-' + base
        return '+***-' + base