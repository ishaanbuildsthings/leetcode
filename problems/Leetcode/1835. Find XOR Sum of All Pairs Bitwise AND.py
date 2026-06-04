class Solution:
    def getXORSum(self, arr1: List[int], arr2: List[int]) -> int:
        LOG = 32
        c1 = [0] * LOG
        c2 = [0] * LOG
        for v in arr1:
            for b in range(LOG):
                if (1 << b) & v:
                    c1[b] += 1
        for v in arr2:
            for b in range(LOG):
                if (1 << b) & v:
                    c2[b] += 1
        
        res = 0

        for v in arr1:
            for b in range(LOG):
                if not (1 << b) & v:
                    continue
                setInArr2 = c2[b]
                if setInArr2 % 2 == 1:
                    res ^= (1 << b)
        
        return res