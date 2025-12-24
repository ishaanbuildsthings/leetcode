import functools

t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    
    # returns the minimum answer for i... just for the 2*a_i*a_j portion in the expanded (a_i + a_j) ^ 2
    # a^2 + b^2 + 2ab for all pairs
    # so a number will contribute 2*a*prevSum
    @functools.lru_cache(maxsize=None)
    def dp(i, prevASum, prevBSum): # prevBSum is derived value
        if i == n:
            return 0
        a = A[i]
        b = B[i]
        ifNoSwapGain = 2 * a * prevASum + 2 * b * prevBSum + dp(i + 1, prevASum + a, prevBSum + b)
        ifSwapGain = 2 * a * prevBSum + 2 * b * prevASum + dp(i + 1, prevASum + b, prevBSum + a)
        return min(ifNoSwapGain, ifSwapGain)
      
    # each term will get squared `n-1` times and contribute to the sum
    res = 0
    for a, b in zip(A, B):
        res += (n - 1) * a**2
        res += (n - 1) * b**2
    print(dp(0, 0, 0) + res)
