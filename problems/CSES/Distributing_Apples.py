import math
children, apples = map(int, input().split())
MOD = 10**9 + 7

# n choose k:
# imagine we have n options for first pick
# n-1 for second
# and so on until n-k+1 options for the last thing
# but this generates permutations, so divide by k!

# (n * (n - 1) * (n - 2) * ... * (n - k + 1)) / k!

# THAT IS:
# n! / ((n - k)! * k!)
def nChooseKWithMod(n, k, mod):
    fac = [1]
    for v in range(1, n + 1):
        fac.append((fac[-1] * v) % mod)
    numerator = fac[n]
    d1 = fac[n - k]
    d2 = fac[k]
    d = (d1 * d2) % mod

    return numerator * pow(d, mod - 2, mod) % mod

bars = children - 1
stars = apples
total = bars + stars
ways = nChooseKWithMod(total, bars, MOD)
print(ways)

