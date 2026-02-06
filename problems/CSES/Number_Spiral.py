def solve():
    r, c = map(int, input().split())
    r -= 1
    c -= 1
    v = max(r, c)
    before = v**2
    direction = 'rightup' if v % 2 == 0 else 'downleft'
    if direction == 'rightup':
        right = c + 1
        up = v - r
        print(before + right + up)
        return
    down = r + 1
    left = v - c
    print(before + down + left)

t = int(input())
for _ in range(t):
    solve() 