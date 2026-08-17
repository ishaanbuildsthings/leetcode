class Solution:
    def sumOfMultiples(self, n: int) -> int:
        def fn(v):
            facs = n // v
            return v * (facs * (facs + 1) // 2)
        return fn(3) + fn(5) + fn(7) - fn(15) - fn(21) - fn(35) + fn(105)