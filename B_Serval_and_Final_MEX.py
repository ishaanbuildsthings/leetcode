def solve(A):
    # print('===========')
    # print(f'{A=}')
    # If 0 is not in the array, mex the entire array
    if 0 not in A:
        # print(f'0 not in A, mex entire')
        print(1)
        print(f'{1} {len(A)}')
        return
    if A[0] != 0 and A[-1] != 0:
        # print(f'neither boundary is 0')
        # mex just inside
        print(2)
        print(f'{2} {len(A) - 1}')
        print(f'{1} {3}')
        return
    
    # if a boundary is 0, mex it with neighbor to get a non 0 boundary
    count = 0
    ops = []
    if A[0] == 0:
        count += 1
        ops.append([1, 2])
        A = [10] + A[2:]
    if A[-1] == 0:
        count += 1
        ops.append([len(A) - 1, len(A)])
        A.pop()
        A.pop()
        A.append(10)
    # mex inside
    if 0 in A:
        count += 1
        ops.append([2, len(A)])
        A = [10, 10]

    # mex all
    count += 1
    ops.append([1, len(A)])
    print(count)
    for l, r in ops:
        print(f'{l} {r}')
    # Lets have boundaries not be 0, so we can mex inside the boundaries all numbers 
    # If 0 is in the array we need to kill the 0s, find the leftmost and rightmost 0 and MEX them together


t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    solve(A)