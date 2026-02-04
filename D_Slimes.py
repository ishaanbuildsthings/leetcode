# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant
import math

class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        if n == 0:
            self.sparse = []
            self.combineFn = combineFn
            self.log2 = [0]
            return

        BITS = n.bit_length()

        sparse = [[0] * n for _ in range(BITS)]
        sparse[0] = nums[:]

        for log in range(1, BITS):
            half = 1 << (log - 1)
            length = 1 << log
            limit = n - length + 1
            rowPrev = sparse[log - 1]
            row = sparse[log]
            for left in range(limit):
                row[left] = combineFn(rowPrev[left], rowPrev[left + half])

        self.sparse = sparse
        self.combineFn = combineFn

        log2 = [0] * (n + 1)
        for i in range(2, n + 1):
            log2[i] = log2[i >> 1] + 1
        self.log2 = log2

    def query(self, l, r):
        width = r - l + 1
        power = self.log2[width]
        windowWidth = 1 << power
        leftAnswer = self.sparse[power][l]
        rightAnswer = self.sparse[power][r - windowWidth + 1]
        return self.combineFn(leftAnswer, rightAnswer)

fmax = lambda x, y: x if x > y else y
fmin = lambda x, y: x if x < y else y

def solve():
    n = int(input())
    A = list(map(int, input().split()))
    # print('==========')
    # print(f'{A=}')

    mx = SparseTable(A, fmax)
    mn = SparseTable(A, fmin)

    curr = 0
    pf = []
    for v in A:
        curr += v
        pf.append(curr)
    
    def sumQuery(l, r):
        if not l:
            return pf[r]
        return pf[r] - pf[l - 1]

    

    # any slime inside a continuous block is easy as we look at the two edges
    # any slime with a bigger neighbor is easy as it is 1
    # slimes that are local maximum are hard
    # a local max requires some prefix or suffix sum going out from it

    res = [-1] * n
    for i, v in enumerate(A):
        left = 0 if not i else A[i - 1]
        right = 0 if i == n - 1 else A[i + 1]
        if left > v or right > v:
            res[i] = 1
            continue
        
        # print(f'{i=}')

        bestHere = float('inf')
        # I do not have a bigger neighbor
        # . ^ .
        # . . .
        # . ^ ^
        # search left
        if i != 0:
            l = 0
            r = i - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                # subarray is m...i-1
                twoDiff = mx.query(m, i - 1) != mn.query(m, i - 1)
                tot = sumQuery(m, i - 1)
                if tot > v and twoDiff:
                    resI = m
                    l = m + 1
                else:
                    r = m - 1
            if resI is not None:
                dist = i - resI
                bestHere = dist
        # search right
        if i != n - 1:
            # print(f'searching right...')
            l = i + 1
            r = n - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                # print(f'subarray is: {A[i+1:m+1]}')
                twoDiff = mx.query(i + 1, m) != mn.query(i + 1, m)
                tot = sumQuery(i + 1, m)
                # print(f'{tot=} {twoDiff=}')
                if tot > v and twoDiff:
                    resI = m
                    r = m - 1
                else:
                    l = m + 1
            if resI is not None:
                dist = resI - i
                bestHere = min(bestHere, dist)
        
        if bestHere != float('inf'):
            res[i] = bestHere
        
    print(*res)



        # we can search right for the first bigger sum with 2 distinct elements
        # or search left with the same



t = int(input())
for _ in range(t):
    solve()