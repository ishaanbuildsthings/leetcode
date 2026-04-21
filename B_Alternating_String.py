import functools

def solve():
    s = input()
    n = len(s)

    blocks = []
    streak = 1

    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            streak += 1
            continue
        else:
            prev = s[i - 1]
            blocks.append(prev * streak)
            streak = 1
    if streak:
        blocks.append(s[-1] * streak)
    
    # print(blocks)

    # counter by size
    sizeCounter = [0] * max(5, (n + 1))
    for b in blocks:
        sz = len(b)
        sizeCounter[sz] += 1
    
    # any block of size 4 or more cannot be resolved
    if any(sizeCounter[x] for x in range(4, n + 1)):
        print('NO')
        return
    
    # a single block of size 3 is allowed
    if sizeCounter[3] > 1:
        print('NO')
        return
    
    if sizeCounter[3] == 1:
        if not sizeCounter[2]:
            print('YES')
            return
        print('NO')
        return
    
    # if we have >2 blocks of size 2 it fails
    if sizeCounter[2] > 2:
        print('NO')
        return
    
    # all blocks size 1
    if not sizeCounter[2]:
        print('YES')
        return

    # a single block of size 2
    # abba
    if sizeCounter[2] == 1:
        print('YES')
        return
    
    # two blocks of size 2
    print('YES')


        


t = int(input())
for _ in range(t):
    solve()