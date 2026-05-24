class Solution:
    def licenseKeyFormatting(self, s: str, k: int) -> str:
        totalNonDash = sum(char != '-' for char in s)
        firstGroupSize = totalNonDash % k if totalNonDash % k else k
        
        resArr = []
        currStrArr = []
        for i, val in enumerate(s):
            if val == '-':
                continue
            if val.isdigit():
                currStrArr.append(val)
            else:
                currStrArr.append(val.upper())
            if not resArr:
                if len(currStrArr) == firstGroupSize:
                    resArr.append(''.join(currStrArr))
                    currStrArr = []
            else:
                if len(currStrArr) == k:
                    resArr.append(''.join(currStrArr))
                    currStrArr = []
                    
        return '-'.join(resArr)