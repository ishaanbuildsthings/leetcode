def solve():
    # print('-----')
    n, c, k = list(map(int, input().split()))
    A = list(map(int, input().split()))
    A.sort()
    # print(f'{A=}')
    for i in range(n):
        if A[i] > c:
            continue
        used = min(c - A[i], k)
        npower = c + used + A[i]
        c = npower
        k -= used

    print(c)
t = int(input())
for _ in range(t):
    solve()