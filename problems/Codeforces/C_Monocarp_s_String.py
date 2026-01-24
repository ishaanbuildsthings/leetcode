t = int(input())
for _ in range(t):
    n = int(input())
    s = input()
    res = float('inf')
    a = s.count('a')
    b = s.count('b')
    initASurplus = a - b

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
        # we have some surplus amount of a, we need to cut off another surplus
        if str(desired) in rightmost:
            width = i - rightmost[str(desired)]
            res = min(res, width)
        
        rightmost[str(asurplus)] = i
    
    print(res if res != float('inf') and res != len(s) else -1)