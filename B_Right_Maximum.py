# from math import inf
# # TEMPLATE BY LEETGOAT DOT IO
# # ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
# # ✅ Passed https://codeforces.com/contest/2031/submission/359281416
# class MaxSegTree:
#     def __init__(self, arr):
#         self.arr = arr
#         self.n = len(arr)

#         size = 1
#         while size < self.n:
#             size <<= 1
#         self.size = size

#         tree = [(float("-inf"), -1)] * (2 * size)
#         base = size
#         for i, v in enumerate(arr):
#             tree[base + i] = (v, i)
#         for idx in range(size - 1, 0, -1):
#             left = tree[idx << 1]
#             right = tree[(idx << 1) | 1]
#             tree[idx] = right if right[0] >= left[0] else left
#         self.tree = tree

#     def _queryHalfOpen(self, l, r):
#         tree = self.tree
#         l += self.size
#         r += self.size
#         left_ans = (float("-inf"), -1)
#         right_ans = (float("-inf"), -1)
#         while l < r:
#             if l & 1:
#                 v = tree[l]
#                 if v[0] > left_ans[0] or (v[0] == left_ans[0] and v[1] > left_ans[1]):
#                     left_ans = v
#                 l += 1
#             if r & 1:
#                 r -= 1
#                 v = tree[r]
#                 if v[0] > right_ans[0] or (v[0] == right_ans[0] and v[1] > right_ans[1]):
#                     right_ans = v
#             l >>= 1
#             r >>= 1
#         if right_ans[0] > left_ans[0] or (right_ans[0] == left_ans[0] and right_ans[1] > left_ans[1]):
#             return right_ans
#         return left_ans

#     def queryMax(self, l, r):
#         return self._queryHalfOpen(l, r + 1)

#     def pointUpdateAndMutateArray(self, index, newVal):
#         self.arr[index] = newVal
#         tree = self.tree
#         pos = self.size + index
#         tree[pos] = (newVal, index)
#         pos >>= 1
#         while pos:
#             left = tree[pos << 1]
#             right = tree[(pos << 1) | 1]
#             tree[pos] = right if right[0] >= left[0] else left
#             pos >>= 1

#     # returns -1 if nothing in range
#     def leftmostGteX(self, l, r, x):
#             return self._leftmostGteX(1, 0, self.size - 1, l, r, x)

#     def _leftmostGteX(self, node, nodeL, nodeR, l, r, x):
#         if nodeR < l or nodeL > r or self.tree[node][0] < x:
#             return -1
#         if nodeL == nodeR:
#             return nodeL
#         mid = (nodeL + nodeR) >> 1
#         left = self._leftmostGteX(node << 1, nodeL, mid, l, r, x)
#         if left != -1:
#             return left
#         return self._leftmostGteX((node << 1) | 1, mid + 1, nodeR, l, r, x)

#     # returns -1 if nothing in range
#     def rightmostGteX(self, l, r, x):
#         return self._rightmostGteX(1, 0, self.size - 1, l, r, x)

#     def _rightmostGteX(self, node, nodeL, nodeR, l, r, x):
#         if nodeR < l or nodeL > r or self.tree[node][0] < x:
#             return -1
#         if nodeL == nodeR:
#             return nodeL
#         mid = (nodeL + nodeR) >> 1
#         right = self._rightmostGteX((node << 1) | 1, mid + 1, nodeR, l, r, x)
#         if right != -1:
#             return right
#         return self._rightmostGteX(node << 1, nodeL, mid, l, r, x)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    vToI = [[] for _ in range(n + 1)]
    for i, v in enumerate(arr):
        vToI[v].append(i)
    res = 0
    elim = n
    for number in range(n, 0, -1):
        while vToI[number] and vToI[number][-1] > elim:
            vToI[number].pop()
        res += len(vToI[number])
        if vToI[number]:
            elim = vToI[number][0]
    print(res)


t = int(input())
for _ in range(t):
    solve()