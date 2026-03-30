# import itertools
# def solve():
#     n = int(input())
#     perms = itertools.permutations(list(range(1, n + 1)))
#     for p in perms:
#         if all(p[i] % p[i+1] >= (p[i+1] % p[i+2]) for i in range(len(p) - 2)):
#             print(p)

def solve():
    n = int(input())
    res = list(range(1,n+1))
    res = res[::-1]
    print(*res)
t = int(input())
for _ in range(t):
    solve()