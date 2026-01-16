from collections import Counter
t = int(input())

import random

# def rand_array(n=1000, lo=1, hi=100):
#     return [random.randint(lo, hi) for _ in range(n)]

for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))


    # A = rand_array()
    # # print(f'{A=}')
    # n = len(A)


    # print('===============')
    A.sort()
    if len(A) == 2:
        print(*A)
        continue
    # print(f'{A=}')
    minDiff = min(abs(A[i] - A[i + 1]) for i in range(n - 1))
    # print(f'{minDiff=}')
    # s = set()
    # for v in A:
    #     s.add(str(v))
    # if len(s) <= 2:
    #     # print(f'only up to 2 unique numbers, printing sorted order')
    #     print(*A)
    #     continue
    
    for i in range(n - 1):
        if A[i + 1] - A[i] == minDiff:
            # start is i+1..., end is ...i
            start = i + 1
            break
    
    res = []
    for i in range(start, n):
        res.append(A[i])
    for i in range(start):
        res.append(A[i])
    drops = 0
    for i in range(n - 1):
        drops += res[i + 1] < res[i]
    # print(f'DROPS: {drops}')
    print(*res)



    # # 1 1 1 1 2 2 2 3 3 4 4 4 4 4 5 5 5 8 8 9 9

    # c = Counter(str(x) for x in A)

    # res = [None] * n
    # # if smallest or larger number can be part of the minimum, do that with a loss of only 1 point

    # canDo = False
    # # check smallest
    # need2 = A[0] + minDiff
    # if need2 == A[0]:
    #     if c[str(A[0])] >= 2:
    #         canDo = True
    # else:
    #     canDo = True
    
    # if canDo:
    #     res[0] = A[0]
    #     res[-1] = A[0] + minDiff
    #     c[str(A[0])] -= 1
    #     c[str(A[0] + minDiff)] -= 1
    #     remain = []
    #     for k, v in c.items():
    #         remain.extend([int(k)] * v)
    #         remain.sort()
    #         for i in range(1, len(res) - 1):
    #             res[i] = remain[i - 1]
    #     print(*res)
    #     continue
    

    # canDo = False
    # need2 = A[-1] - minDiff
    # if need2 == A[-1]:
    #     if c[str(A[-1])] >= 2:
    #         canDo = True
    # else:
    #     canDo = True
    
    # if canDo:
    #     res[0] = A[-1] - minDiff
    #     res[-1] = A[-1]
    #     c[str(A[-1])] -= 1
    #     c[str(A[-1] - minDiff)] -= 1
    #     remain = []
    #     for k, v in c.items():
    #         remain.extend([int(k)] * v)
    #         remain.sort()
    #         for i in range(1, len(res) - 1):
    #             res[i] = remain[i - 1]
    #     print(*res)
    #     continue
    
    # # print(f'couldnt do with start or finish')
    
    # start = None
    # finish = None
    # for v in A:
    #     if str(v + minDiff) in s:
    #         if (minDiff == 0 and c[str(v)] >= 2) or (minDiff != 0):
    #             res[0] = v
    #             res[-1] = v + minDiff
    #             c[str(v)] -= 1
    #             c[str(v + minDiff)] -= 1
    #             remain = []
    #             # print(f'initialized resuult: {res}')
    #             for k, v in c.items():
    #                 remain.extend([int(k)] * v)
    #             remain.sort()
    #             for i in range(1, len(res) - 1):
    #                 res[i] = remain[i - 1]

    # if n >= 4:
    #     if res[1] < res[0] and res[-1] < res[-2]:
    #         res[1], res[-2] = res[-2], res[1]
    # print(*res)

    


    # # res = [None] * n
    # # for v in A:
    # #     if str(v + minDiff) in s:
    # #         res[0] = v
    # #         res[-1] = v + minDiff
    # #         c[str(v)] -= 1
    # #         c[str(v + minDiff)] -= 1
    # #         break
    
    # # print(f'init setup: {res=}')