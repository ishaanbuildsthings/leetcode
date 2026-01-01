import collections
n = int(input())
A = list(map(int, input().split()))
MOD = 10**9 + 7
count = collections.Counter(A)
res = 1
for k, v in count.items():
    res *= v + 1
    res %= MOD
print(res - 1)
