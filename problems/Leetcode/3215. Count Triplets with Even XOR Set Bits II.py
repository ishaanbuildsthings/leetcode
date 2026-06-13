class Solution:
    def tripletCount(self, a: List[int], b: List[int], c: List[int]) -> int:
        oddA = evenA = oddB = evenB = oddC = evenC = 0
        for v in a:
            if v.bit_count() % 2:
                oddA += 1
            else:
                evenA += 1
        for v in b:
            if v.bit_count() % 2:
                oddB += 1
            else:
                evenB += 1
        for v in c:
            if v.bit_count() % 2:
                oddC += 1
            else:
                evenC += 1
        
        res = 0
        res += evenA * evenB * evenC
        res += oddA * oddB * evenC
        res += oddA * evenB * oddC
        res += evenA * oddB * oddC

        return res
        
