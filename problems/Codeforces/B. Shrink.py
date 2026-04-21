import sys
input = sys.stdin.readline
 
t = int(input())
for _ in range(t):
    n = int(input())
    # print(f'test case n={n}')
 
    resArr = [None] * n
    isLeft = True
    distFromEndpoint = 0
    for number in range(1, n + 1):
        if isLeft:
            resArr[distFromEndpoint] = number
            isLeft = False
 
        else:
            resArr[n - distFromEndpoint - 1] = number
            isLeft = True
            distFromEndpoint += 1
 
        # isLeft = not isLeft
 
    print(' '.join(map(str, resArr)))
 
 
 
    # 1 3 2 -> 1 peak for 3 elements
    # 1 3 4 2 -> 1 peak for 4 elements
    # 1 3 2 5 4 -> 2 peaks for 5 elements
    # 1   2