from functools import cmp_to_key
class Solution:
    def minimumEffort(self, tasks: List[List[int]]) -> int:
        
        def cmp(A, B):
            # starting energy needed if we do A before B
            aBeforeB = max(A[1], B[1] + A[0])
            bBeforeA = max(B[1], A[1] + B[0])
            if aBeforeB <= bBeforeA:
                return -1
            return 1
        
        tasks.sort(key=cmp_to_key(cmp))

        res = 0
        currEnergy = 0
        for actual, mn in tasks:
            if currEnergy < mn:
                diff = mn - currEnergy
                currEnergy = mn
                res += diff
            currEnergy -= actual
        
        return res