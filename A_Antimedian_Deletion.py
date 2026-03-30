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

    # res = [None] * len(a)
    # for i, v in enumerate(a):
    #     # print('--')
    #     # print(f'{i=}')
    #     na = a[:]
    #     # print/(f'{na=}')
    #     while len(na) >= 3 and v not in na[:3]:
    #         big = max(na[:3])
    #         na.pop(na.index(big))
    #     while len(na) >= 3 and v in na[:3]:
    #         big = max(na[:3])
    #         if big != v:
    #             na.pop(na.index(big))
    #         else:
    #             break
    #     # print(f'step 2')
    #     while len(na) >= 3 and v not in na[:-3]:
    #         # print(f'na is: {na}')
    #         big = max(na[-3:])
    #         na.pop(na.index(big))
    #     while len(na) >= 3 and v
    #     res[i] = len(na)
    # print(*res)
