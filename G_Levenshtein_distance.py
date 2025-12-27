import functools

a = input()
b = input()

# print(f'{a=}')
# print(f'{b=}')

abc = 'abcdefghijklmnopqrstuvwxyz'
cToCost = {
    c : i + 1 for i, c in enumerate(abc)
}

@functools.lru_cache(maxsize=None)
def dp(i, j):
    if i == len(a) and j == len(b):
        return 0
    if i == len(a):
        return cToCost[b[j]] + dp(i, j + 1)
    if j == len(b):
        return cToCost[a[i]] + dp(i + 1, j)
    if a[i] == b[j]:
        return dp(i + 1, j + 1)
    dist = abs(cToCost[b[j]] - cToCost[a[i]])
    ifSub = dist + dp(i + 1, j + 1)

    ifDelTop = cToCost[a[i]] + dp(i + 1, j)

    ifDelBottom = cToCost[b[j]] + dp(i, j + 1)

    return min(ifSub, ifDelTop, ifDelBottom)

print(dp(0, 0))
    