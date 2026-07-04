class Solution:
    def findInteger(self, k: int, digit1: int, digit2: int) -> int:
        res = inf
        for size in range(12):
            for mask in range(1 << size):
                num = 0
                broke = False
                for bit in range(size):
                    num *= 10
                    if mask & (1 << bit):
                        num += digit1
                    else:
                        num += digit2
                    if num >= 2**31:
                        broke = True
                        break
                if broke: continue
                if num % k == 0 and num > k:
                    res = min(res, num)
        return res if res != inf else -1