# can precompute squares in sqrt time and store in a set and check, instead of recomputing b
# can use two pointers and increment greedily to reach the target
class Solution:
    def judgeSquareSum(self, c: int) -> bool:
        for a in range(int(math.floor(math.sqrt(c))) + 1):
            b = math.sqrt(c - a**2)
            if b == math.floor(b):
                return True
        return False