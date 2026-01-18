from collections import Counter
def solve(s, k):
    if s < s[::-1]:
        return True
    if k == 0:
        return False
    c = Counter(s)
    if len(c.keys()) == 1:
        return False
    # there is at least 2 distinct letters and we have a swap
    return True
t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    s = input()
    print("YES" if solve(s, k) else "NO")