def solve():
    r, g, b = list(map(int, input().split()))
    resArr = []    
    while True:
        # big biggest frequency first
        opts = sorted([(r, 'R'), (g, 'G'), (b, 'B')], reverse=True)
        ok = False
        for v, letter in opts:
            if not v:
                break
            if resArr and resArr[-1] == letter:
                continue
            if len(resArr) >= 3 and resArr[-3] == letter:
                continue
            resArr.append(letter)
            r -= letter == 'R'
            g -= letter == 'G'
            b -= letter == 'B'
            ok = True
        if not ok:
            break
    
    print(''.join(resArr))

t = int(input())
for _ in range(t):
    solve()