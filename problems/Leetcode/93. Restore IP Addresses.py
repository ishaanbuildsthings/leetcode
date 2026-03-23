class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        if len(s) > 12:
            return []
        
        def valid(strnum):
            if len(strnum) > 1 and strnum[0] == '0':
                return False
            v = int(strnum)
            if v > 255:
                return False
            return True
        
        res = []

        for s1 in range(1, 4):
            if s1 > len(s):
                break
            for s2 in range(1, 4):
                if s1 + s2 > len(s):
                    break
                for s3 in range(1, 4):
                    if s1 + s2 + s3 > len(s):
                        break
                    s4 = len(s) - (s1 + s2 + s3)
                    if s4 <= 0:
                        break
                    
                    str1 = s[:s1]
                    str2 = s[s1:s1+s2]
                    str3 = s[s1+s2:s1+s2+s3]
                    str4 = s[s1+s2+s3:]

                    if not valid(str1) or not valid(str2) or not valid(str3) or not valid(str4):
                        continue
                    
                    res.append(str1 + '.' + str2 + '.' + str3 + '.' + str4)
        
        return res


