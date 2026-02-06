def solve():
    n = int(input())
    s = input()
    pf = 0
    suff = 0
    gaps = []
    streak = 0
    for i, v in enumerate(s):
        if v == '0':
            streak += 1
            continue
        if streak:
            gaps.append(streak)
        streak = 0
    if streak:
        gaps.append(streak)
    
    if gaps and s[0] == '0':
        pf = gaps[0]
        gaps.pop(0)
    if gaps and s[-1] == '0':
        suff = gaps[-1]
        gaps.pop()
    
    # all 0s
    # 1->1
    # 2->1
    # 3->1
    # 4->2
    # 5->2
    # 6->2 0 1 0 0 1 0
    # 7->3 0 1 0 0 1 0 1
    if max(int(x) for x in s) == 0:
        if n % 3 == 0:
            print(n // 3)
        else:
            print(n // 3 + 1)
        return
    
    res = 0

    # handle prefix + suffix
    res += (pf + 1) // 3
    res += (suff + 1) // 3

    # 1-> 0   0 |
    # 2-> 1   1 0 |
    # 3-> 1   0 1 0 |
    # 4-> 1   0 1 0 0 |
    # 5-> 2   0 1 0 1 0 |
    # 6-> 2
    # 7-> 2

    # handle gaps
    # 1 -> 0    1 0 1
    # 2 -> 0    1 0 0 1
    # 3 -> 1    1 0 1 0 1
    # 4 -> 1    1 0 0 1 0 1
    # 5 -> 1    1 0 0 1 0 0 1
    # 6 -> 2    1 0 0 1 0 1 0 1
    for g in gaps:
        res += g // 3
    
    print(res + sum(x == '1' for x in s))



t = int(input())
for _ in range(t):
    solve()