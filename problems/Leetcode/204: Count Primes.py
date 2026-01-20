class Solution:
    def countPrimes(self, n: int) -> int:
        if n <= 1:
            return 0
        isPrime = [True] * n
        isPrime[0] = False
        isPrime[1] = False
        # some bullshit to let us iterate by 2 in the next loop
        for v in range(4, n, 2):
            isPrime[v] = False

        for div in range(3, math.ceil(math.sqrt(n)), 2): # sqrt can help speed up
            if not isPrime[div]:
                continue
            for mult in range(div * div, n, div): # div * div trick can help speed up
                isPrime[mult] = False

        return sum(isPrime) # no generator python speedup lol
