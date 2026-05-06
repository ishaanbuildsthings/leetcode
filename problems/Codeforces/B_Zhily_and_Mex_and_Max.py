from collections import defaultdict
def solve():
    n = int(input())
    A = list(map(int, input().split()))
    mx = max(A)

    if mx == 0:
        print(n)
        return

    counts = defaultdict(int)
    for v in A:
        counts[str(v)] += 1

    score = mx * n

    chain = 0 # we have built this size chain

    for i in range(1, n):
        if counts[str(chain)]:
            chain += 1
        if chain == mx:
            chain += 1
        score += chain
    
    print(score)

    
    # print(f'{chain=}')
t = int(input())
for _ in range(t):
    solve()