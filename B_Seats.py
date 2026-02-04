def solve():
    n = int(input())
    s = input()
    # print('=====')
    # print(f'{s=}')
    lst = list(s)
    A = [int(x) for x in lst]
    if max(A) == 0:
        print((n+2)//3)
        return
    res = sum(A)
    pf = 0
    for i, v in enumerate(A):
        if not v:
            pf += 1
        else:
            break
    sf = 0
    for i, v in enumerate(A[::-1]):
        if not v:
            sf += 1
        else:
            break
    
    seen = False
    streak = 0
    gaps = []
    for i, v in enumerate(A):
        if not seen:
            if v == 1:
                seen = True
            continue
        if v == 1:
            if streak:
                gaps.append(streak)
            streak = 0
            continue
        streak += 1

    # print(gaps)
    # print(f'{pf=} {sf=}')
    res += (pf+1)//3
    res += (sf+1)//3
    for g in gaps:
        res += (g)//3
    print(res)


        
    


t = int(input())
for _ in range(t):
    solve()

# 0 0 0 0 0 0

# 3, 4 -> 1
# 5, 6 -> 2

# 2,3 // 2 -> 1
# 4,5 // 2 -> 2