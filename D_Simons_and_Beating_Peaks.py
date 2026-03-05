from math import inf
def solve():
    print('--------')
    n = int(input())
    arr = list(map(int, input().split()))
    print(f'{arr=}')
    # we are good if we go straight up
    # straight down
    # or are a V


    # for every local peak, we can destroy both elft and right to make this a divot
    # but only one must be the divot
    # pick which index is a divot, everything on the left simply destroys left only, right destroys right only

    # index of first left that is greater
    leftGreater = [-1] * n
    stack = [] # decreasing
    for i, v in enumerate(arr):
        while stack and arr[i] > arr[stack[-1]]:
            popped = stack.pop()
        if stack:
            leftGreater[i] = stack[-1]
        stack.append(i)
    
    print(f'{leftGreater=}')

    rightGreater = [n] * n
    stack = [] # decreasing
    for i in range(n - 1, -1, -1):
        while stack and arr[i] > arr[stack[-1]]:
            stack.pop()
        if stack:
            rightGreater[i] = stack[-1]
        stack.append(i)
    
    print(f'{rightGreater=}')

    mx = max(arr)
    mxI = arr.index(mx)
    print(f'{mxI=}')


    # disappear all on right, then repeatedly chain on left
    goneRight = n - mxI - 1
    

t = int(input())
for _ in range(t):
    solve()