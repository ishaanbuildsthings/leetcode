t = int(input())
for _ in range(t):
    n, h, l = map(int, input().split())
    A = list(map(int, input().split()))
    # print('==========')
    # print(f'{h=} {l=}')
    A.sort()
    # print(f'{A=}')
    res = 0

    maxPairs = n // 2
    for pairs in range(maxPairs + 1):
        # can we form 10 pairs?
        # 10 numbers <= tight
        # 10 numbers <= loose
        halfway = A[pairs - 1]
        full = A[2 * pairs - 1]
        if halfway <= min(h, l) and full <= max(h, l):
            res = pairs
    
    print(res)
