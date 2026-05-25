def solve():
    n = int(input())
    A = list(map(int, input().split()))
    ops = []
    flipped = 0
    for i in range(n - 1, -1, -1):
        val = A[i] if not flipped else -1 * A[i]
        if val > 0:
            ops.append(i + 1)
            flipped ^= 1
        else:
            continue
    print(len(ops))
    print(*ops)
t = int(input())
for _ in range(t):
    solve()
