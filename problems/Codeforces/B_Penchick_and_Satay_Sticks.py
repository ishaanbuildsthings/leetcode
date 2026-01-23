def solve(A):
    n = len(A)
    for i in range(n - 1):
        if A[i] == i + 1:
            continue
        if abs(A[i] - A[i + 1]) != 1:
            print("NO")
            return
        A[i], A[i + 1] = A[i + 1], A[i]
        if A[i] != i + 1:
            print("NO")
            return
    
    print("YES")
            
t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    # A = [1, 3, 2]
    # A = [2, 1, 3, 5, 4]
    solve(A)
