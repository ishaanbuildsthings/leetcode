T = int(input())
for _ in range(T):
    n = int(input())
    # print('=======')
    s = input()
    # print(f'{s=}')
    # find a 0 that is furthest from the previous left 1
    res = 0

    for i in range(n - 1, -1, -1):
        if s[i] == '1':
            rightmost = i
            break

    before = rightmost - n
    # print(f'{before=}')

    for i in range(n):
        if s[i] == '1':
            before = i
            continue
        gaps = i - before
        res = max(res, gaps)
    
    print(res)
