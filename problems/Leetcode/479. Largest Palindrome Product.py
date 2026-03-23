# class Solution:
#     def largestPalindrome(self, n: int) -> int:
#         if n == 1:
#             return 9

#         # max size palindrome is 2*n digits

#         upper = 10**n - 1 # max first half
#         lower = 10**(n-1)
#         for prefix in range(upper, -1, -1):
#             pal = int(str(prefix) + str(prefix)[::-1])
#             for number in range(upper, lower - 1, -1):
#                 if pal // number > upper:
#                     break
#                     # if the second factor (which can only get bigger and bigger) becomes too big we stop

#                 # if the first number of length n is a factor
#                 if pal % number == 0:
#                     # if the second factor is also length n
#                     if len(str(pal // number)) == n:
#                         return pal % 1337

class Solution:
    def largestPalindrome(self, n: int) -> int:
        if n == 1:
            return 9
        upper = 10 ** n - 1
        m = (n + 1) // 2
        lower = upper - 10 ** m

        valid = {1, 3, 7, 9}

        # go from like 999 -> 997
        def prevValid(x):
            x -= 1
            while x > lower and x % 10 not in valid:
                x -= 1
            return x

        heap = [(-upper * upper, upper, upper)] # heap stores (product, num1, num2)
        seen = {(upper, upper)}

        while heap:
            negProd, i, j = heapq.heappop(heap)
            prod = -negProd
            s = str(prod)
            if s == s[::-1]:
                return prod % 1337

            for ni, nj in [(i, prevValid(j)), (prevValid(i), j)]:
                a, b = max(ni, nj), min(ni, nj)
                if a > lower and b > lower and (a, b) not in seen:
                    seen.add((a, b))
                    heapq.heappush(heap, (-a * b, a, b))

        return 0