from collections import deque
from math import gcd
def solve():
    l, r, g = map(int, input().split())
    # find smallest multiple of G >= L
    if l % g == 0:
        l2 = l
    else:
        fulls = l // g
        l2 = (fulls * g) + g
    if r % g == 0:
        r2 = r
    else:
        remain = r % g
        r2 = r - remain

    if l2 > r2:
        print(f'{-1} {-1}')
        return
    
    q = deque()
    q.append((l2, r2))
    seen = {(l2, r2)}
    while q:
        l3, r3 = q.popleft()
        if gcd(l3, r3) == g:
            print(f'{l3} {r3}')
            return
        if (l3, r3 - g) not in seen and l3 <= r3 - g and r3 - g >= l:
            seen.add((l3, r3 - g))
            q.append((l3, r3 - g))
        if (l3 + g, r3) not in seen and l3 + g <= r3 and l3 + g <= r:
            seen.add((l3 + g, r3))
            q.append((l3 + g, r3))
    print(f'{-1} {-1}')

t = int(input())
for _ in range(t):
    solve()
