import functools

n = int(input())
B = []
for _ in range(n):
    B.append(int(input()))
print(f'{B=}')


# The smallest ending digit we can get
@functools.lru_cache(maxsize=None)
def dp(i, prevDigit):
    if i == n:
        return prevDigit
    for nextDigit in range(prevDigit + 1, prevDigit + 12):
        tot = sum(int(x) for x in str(nextDigit))
        if tot != B[i]:
            continue
        
