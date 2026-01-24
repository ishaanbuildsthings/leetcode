t = int(input())
for _ in range(t):
    n = int(input())
    s = input()
    # print('================')
    # print(f'{s=}')
    res = float('inf')
    a = s.count('a')
    b = s.count('b')
    # print(f'{a=} {b=}')
    initASurplus = a - b

    # print(f'{initASurplus=}')

    if initASurplus == 0:
        print('0')
        continue

    # say we have 5 more A's than B's
    # we need to cut out a surplus of 5 a's somewhere, in as short a string as possible
    # if our prefix has a surplus of 7 we need to cut out the rightmost surplus of 2

    asurplus = 0
    rightmost = { '0' : - 1 }
    for i, v in enumerate(s):
        if v == 'a':
            asurplus += 1
        else:
            asurplus -= 1
        desired = asurplus - initASurplus
        # print(f'a surplus now: {asurplus}, desired: {desired}')
        # we have some surplus amount of a, we need to cut off another surplus
        if str(desired) in rightmost:
            # print(f'a prefix with that desired exists')
            width = i - rightmost[str(desired)]
            # print(f'the width makes: {width}')
            res = min(res, width)
        
        rightmost[str(asurplus)] = i
    
    print(res if res != float('inf') and res != len(s) else -1)