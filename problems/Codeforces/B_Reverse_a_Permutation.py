def solve():
    n = int(input())
    A = list(map(int, input().split()))
    for i in range(n):
        hope = n - i
        if A[i] == hope:
            continue
        loc = A.index(hope)
        # flip i...loc
        newA = A[:i] + A[i:loc + 1][::-1] + A[loc + 1:]
        print(*newA)
        return
    
    print(*A)

t = int(input())
for _ in range(t):
    solve()

        