
class Solution:
    def threeFibonacciSum(self, n: int) -> bool:
        if n % 2:
            return False
        half = n // 2

        fibs = [1, 1]
        while fibs[-1] < half:
            fibs.append(fibs[-1] + fibs[-2])

        print(fibs)

        if fibs[-1] == half:
            return True

        return False
        