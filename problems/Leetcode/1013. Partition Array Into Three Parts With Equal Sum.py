class Solution:
    def canThreePartsEqualSum(self, arr: List[int]) -> bool:
        tot = sum(arr)
        if tot % 3:
            return False
        
        curr = 0
        for i in range(len(arr)):
            curr += arr[i]
            if curr == tot / 3:
                curr2 = 0
                for j in range(i + 1, len(arr) - 1):
                    curr2 += arr[j]
                    if curr2 == tot / 3:
                        return True
                return False
        
        return False