def solve():
    n = int(input())
    A = list(map(int, input().split()))
        # mx = n
    for i in range(n):
        hope = n - i
        if A[i] == hope:
            continue
        loc = A.index(hope)
        # print(f'loc={loc}')
        # flip i...loc
        newA = A[:i] + A[i:loc + 1][::-1] + A[loc + 1:]
        print(*newA)
        return
    
    print(*A)

t = int(input())
for _ in range(t):
    solve()

        