import bisect
from collections import Counter

def countInRange(arr, l, r):
    if l > r:
        return 0
    left = bisect.bisect_left(arr, l)
    right = bisect.bisect_right(arr, r)
    return right - left

def nc3(n):
    return int(n * (n-1) * (n-2) / 6)

def nc2(n):
    return int(n * (n - 1) / 2)
fmax = lambda x, y: x if x > y else y
def solve(A):
    # print('=========')
    # print(f'{A=}')
    A.sort()
    c = Counter(A)
    res = 0
    mx = A[-1]
    for i in range(len(A)):
        a = A[i]
        for j in range(i + 1, len(A) - 1):
            # print(f'{i=}, {j=}')
            b = A[j]
            maxC = a + b - 1
            minC = mx - a - b + 1
            minC = fmax(minC, b + 1) # only take elements > b, we will handle b separately
            # print(f'minC: {minC} maxC: {maxC}')
            cnt = countInRange(A, minC, maxC)
            # print(f'count: {cnt}')
            res += cnt

            # if a + b + b > mx:
            #     print(f'could take a b though')
            #     res += c[b]
            #     print(f'count of that is: {c[b]}')
            #     res -= 1
            #     if a == b:
            #         res -= 1
            #     print(f'res now: {res}')

    # any triple that sums to > mx works
    for key in c.keys():
        if c[key] >= 3:
            if key * 3 > mx:
                ways = nc3(c[key])
                res += ways
    
    # print(f'res after triplets: {res}')

    keys = sorted(c.keys())

    # any number + pair works if the sum is > mx
    for i in range(len(keys)):
        low = keys[i]
        for j in range(i + 1, len(keys)):
            # pick 1 low, 2 high
            high = keys[j]
            if c[high] >= 2 and high + high + low > mx:
                ways = c[low] * nc2(c[high])
                res += ways


            

    return res


# Iterate on the smallest 2 numbers I pick, A and B
# I cannot take a C >= A + B or Bob will color that
# If I take a smaller C, Bob can take the max, so I need a C such that A + B + C > MAX

# max C I can take: A + B - 1
# min C I can take: MAX - A - B + 1
# min C must also be >= B

t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    print(solve(A))





# import random

# def genRandomArray(size, low, high):
#     return sorted([random.randint(low, high) for _ in range(size)])


# def brute(A):
#     res = 0
#     mx = max(A)
#     for i in range(len(A)):
#         for j in range(i+1, len(A)):
#             for k in range(j+1, len(A)):
#                 if A[i] + A[j] + A[k] > mx:
#                     if A[k] < A[i] + A[j]:
#                         res += 1
#     return res


# for _ in range(100):
#     r = genRandomArray(100, 1, 20)
#     b = brute(r)
#     my = solve(r)
#     if b != my:
#         print("FAIL")