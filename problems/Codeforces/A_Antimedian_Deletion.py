t = int(input())
for _ in range(t):
    # print('----------')
    n = int(input())
    a = list(map(int, input().split()))

    if len(a) == 1:
        print(*[1])
        continue
    
    if len(a) == 2:
        print(*[2, 2])
        continue
    
    res = [2] * len(a)
    print(*res)