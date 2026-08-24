fibs = [1, 1]
while fibs[-1] < 10**9:
    fibs.append(fibs[-2] + fibs[-1])

# can do in O(1) space by computing the biggest two fib numbers <= k, then descending back down
class Solution:
    def findMinFibonacciNumbers(self, k: int) -> int:
        remain = k
        i = len(fibs) - 1
        res = 0
        while remain:
            if fibs[i] > remain:
                i -= 1
                continue
            remain -= fibs[i]
            res += 1
            i -= 1
        return res
