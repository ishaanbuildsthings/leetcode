n, x, y, z = map(int, input().split())
import functools

clip1 = (1 << (x + 1)) - 1
clip2 = (1 << (y + 1)) - 1
clip3 = (1 << (z + 1)) - 1

MOD = 10**9 + 7

@functools.cache
def dp(i, reach1, reach2, reach3, hasHaiku):
  if i == n:
    return int(hasHaiku)
  res = 0
  for d in range(1, 11):
    seed2 = (1 << d) if reach1 & (1 << x) else 0
    seed3 = (1 << d) if reach2 & (1 << y) else 0
    nreach1 = ((reach1 << d) | (1 << d)) & clip1
    nreach2 = ((reach2 << d) | seed2) & clip2
    nreach3 = ((reach3 << d) | seed3) & clip3
    nhas = hasHaiku or bool(nreach3 & (1 << z))
    res += dp(i + 1, nreach1, nreach2, nreach3, nhas)
    res %= MOD
  return res

print(dp(0, 0, 0, 0, False))