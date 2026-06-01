class Solution:
    def isPowerOfThree(self, n: int) -> bool:
        curr = 1
        
        while curr <= n:
            if curr == n: return True
            curr *= 3

        return False