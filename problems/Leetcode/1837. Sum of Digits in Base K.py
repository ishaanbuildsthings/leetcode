class Solution:
    def sumBase(self, n: int, k: int) -> int:
        curr = n
        res = 0
        while curr:
            remain = curr % k
            res += remain
            curr //= k
        return res