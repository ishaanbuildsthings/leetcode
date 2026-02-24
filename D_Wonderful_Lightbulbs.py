from collections import defaultdict
t = int(input())
for _ in range(t):
    n = int(input())
    points = []
    x = defaultdict(int)
    xy = defaultdict(int)
    for _ in range(n):
        a, b = map(int, input().split())
        a = str(a)
        b = str(b)
        x[a] += 1
        xy[str(int(a) + int(b))] += 1
    X = None
    for k, v in x.items():
        if v % 2:
            X = int(k)
    # print(f'{X=}')
    XY = None
    for k, v in xy.items():
        if v % 2:
            XY = int(k)
    Y = XY - X
    print(f'{X} {Y}')
