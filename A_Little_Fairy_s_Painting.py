T = int(input())
for _ in range(T):
    # print('=======')
    n = int(input())
    A = list(map(int, input().split()))
    # print(f'{n=} {A=}')
    s = set()
    for v in A:
        s.add(str(v))
    res = float('inf')
    for v in A:
        if v >= len(s):
            res = min(res, v)
    print(res)