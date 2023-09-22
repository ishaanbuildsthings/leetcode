
# RETURNS A LIST OF OF FROM [0, n-1] OF IF A NUMBER IS PRIME OR NOT
def countPrimes(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 0

    sieve = [True for _ in range(n)]
    sieve[0] = False
    sieve[1] = False
    res = 0
    for i in range(2, n):
        if sieve[i]:
            res += 1
        else:
            continue # linear optimization
        for j in range(i * i, n, i): # square optimization since all multiples of i less than i*i would have been marked
            sieve[j] = False
    return sieve