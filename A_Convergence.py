from collections import Counter
from math import inf
def solve():
    n = int(input())
    A = list(map(int, input().split()))
    A.sort()
    # print(f'{A=}')

    res = inf

    
    # solve at this index
    for i, v in enumerate(A):
        # frq = Counter(A)
        pool = [x for x in A if x != v]
        # print(f'{pool=}')
        l = 0
        r = len(pool) - 1
        pairs = 0
        while l <= r:
            if pool[l] <= v and pool[r] >= v:
                pairs += 1
                l += 1
                r -= 1
            else:
                break
        score = pairs + (r - l + 1)
        res = min(res, score)
    
    print(res)




t = int(input())
for _ in range(t):
    solve()