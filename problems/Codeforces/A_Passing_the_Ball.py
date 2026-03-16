def solve():
    n = int(input())
    s = input()
    passes = n
    i = 0
    seen = set()
    seen.add(0)
    while passes:
        if s[i] == 'R':
            i += 1
        else:
            i -= 1
        seen.add(i)
        passes -= 1
    print(len(seen))

t = int(input())
for _ in range(t):
    solve()