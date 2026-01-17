def solve(A):
    for i in range(len(A) - 1):
        if abs(A[i] - A[i+1]) <= 1:
            return 0
    if len(A) == 2:
        return -1
    if A == sorted(A):
        return -1
    if A == sorted(A)[::-1]:
        return -1
    return 1
    
t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    print(solve(A))



    # 1 10 20 30



    # 1 3 5

    # all strict up is unfixable


    # 1 3 5 10


    # all strict down is indexToConsider

    # 10 5 3 1


    # 1 5 3