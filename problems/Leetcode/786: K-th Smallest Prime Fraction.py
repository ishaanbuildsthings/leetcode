class Solution:
    def kthSmallestPrimeFraction(self, arr: List[int], k: int) -> List[int]:
        # binary search on answer
        l = 0
        r = 1
        res = None
        EPSILON = 10**(-10)
        while l + EPSILON <= r:
            m = (l + r) / 2
            # how many fractions are <= m?
            count = 0
            # biggest fraction <= m?
            biggest = 0
            biggestArr = None
            # pointers
            # as L increases, R monotonically increases
            R = 0
            for L, numerator in enumerate(arr):
                numerator = arr[L]
                # increase the fraction while invalid
                while R < len(arr) and numerator / arr[R] > m:
                    R += 1
                
                # R is valid now (or out of bounds)
                gain = len(arr) - R
                count += gain

                if R < len(arr):
                    fraction = numerator / arr[R]
                    if fraction > biggest:
                        biggest = fraction
                        biggestArr = [numerator, arr[R]]
                
            if count >= k:
                r = m
                res = biggestArr
            else:
                l = m
        return res

                




        # O(n^2 log n brute force)
#         # stores tuples [fraction, arr[i], arr[j]]
#         data = []
#         for i in range(len(arr)):
#             for j in range(i + 1, len(arr)):
#                 frac = arr[i] / arr[j]
#                 data.append([frac, arr[i], arr[j]])
#         data.sort()
#         return [data[k - 1][1], data[k - 1][2]]



# # each row is sorted, but not necessarily each column

# # 1 a b c d
# # 2 e f g h
# # 3 i j k l
# # 5 m n o p
# #   1 2 3 5


# # 1        0.5  0.33  0.2
# # 2              0.66  0.4
# # 3                    0.6
# # 5
# #       1    2    3    5