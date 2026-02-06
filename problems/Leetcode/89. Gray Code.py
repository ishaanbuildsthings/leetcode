# class Solution:
#     def grayCode(self, n: int) -> List[int]:
#         if n == 0:
#             return [0]
#         smallerGray = self.grayCode(n - 1)
#         added = 2**(n-1)
#         newGrey = [x + added for x in smallerGray][::-1]
#         return smallerGray + newGrey

class Solution:
    def grayCode(self, n: int) -> List[int]:
        res = []
        for i in range(1 << n):
            res.append(i ^ (i >> 1))
        return res