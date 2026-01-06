n = int(input())
A = list(map(int, input().split()))
curr = 0
res = float('-inf')
for v in A:
    res = max(res, curr + v)
    curr = max(0, curr + v)
print(res)

# can also be written like this:
# class Solution:
#     def maxSubArray(self, nums: List[int]) -> int:
#         fmax = lambda x, y: x if x > y else y

#         res = -inf
#         currMax = -inf
#         for v in nums:
#             currMax = fmax(currMax + v, v)
#             res = fmax(res, currMax)
#         return res