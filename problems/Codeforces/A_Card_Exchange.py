from collections import Counter
t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    A = list(map(int, input().split()))

    c = Counter(A)
    # any frequency >= K we group with the next frequency and can cull that entire section to k-1
    
    frqs = sorted(c.values(), reverse=True)
    if frqs[0] < k:
        print(n)
    else:
        print(k - 1)

