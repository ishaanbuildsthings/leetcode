def solve():
    s = input()
    res = 0
    n = len(s)
    mxSize = n if n % 2 == 0 else n - 1
    for doubleSize in range(mxSize, 0, -2):
        size = doubleSize // 2
        matches = 0
        for i in range(size):
            left = s[i]
            right = s[i + size]
            if left == '?' or right == '?' or left == right:
                matches += 1
        if matches == size:
            print(size * 2)
            return
        for r in range(2 * size, n, 1):
            gained = s[r]
            lost = s[r - 2 * size]
            gainMatch = 0
            if s[r] == s[r - size] or s[r] == '?' or s[r - size] == '?':
                gainMatch = 1
            lostMatch = 0
            if s[r - 2 * size] == '?' or s[r - size] == '?' or s[r - size] == s[r - 2 * size]:
                lostMatch = 1
            matches += gainMatch
            matches -= lostMatch
            if matches == size:
                print(size * 2)
                return
    print(0)
t = int(input())
for _ in range(t):
    solve()