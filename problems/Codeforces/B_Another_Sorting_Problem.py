from math import inf
def solve():
    n = int(input())
    A = list(map(int, input().split()))
    minToAdd = -inf
    for i in range(1, n):
        if A[i] < A[i-1]:
            diff = A[i-1]-A[i]
            minToAdd = max(minToAdd,diff)
    if minToAdd == -inf:
        print('YES')
        return
    print(f'{minToAdd=}')
    for i in range(1, n):
        if A[i] < A[i-1]:
            A[i] += minToAdd
            if A[i] < 
        
        

t = int(input())
for _ in range(t):
    solve()